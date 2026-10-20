"""Fusion DoRA sûre : ligne de norme nulle (canal mort de la base), story C3."""

from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")
peft = pytest.importorskip("peft")

from slmsp.train.export import norme_dora_sure  # noqa: E402


def _modele_dora() -> torch.nn.Module:
    class Petit(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.proj = torch.nn.Linear(8, 6, bias=False)

    base = Petit()
    with torch.no_grad():
        base.proj.weight[2].zero_()  # canal mort
    config = peft.LoraConfig(r=2, lora_alpha=4, target_modules=["proj"], use_dora=True)
    return peft.get_peft_model(base, config)


def test_fusion_dora_ligne_nulle_finie() -> None:
    torch.manual_seed(0)
    modele = _modele_dora()
    with norme_dora_sure():
        fusionne = modele.merge_and_unload()
    poids = fusionne.proj.weight
    assert bool(torch.isfinite(poids).all())
    assert float(poids[2].abs().max()) == 0.0


def test_fusion_dora_sans_garde_non_finie_et_methode_restauree() -> None:
    from peft.tuners.lora.dora import DoraLinearLayer

    avant = DoraLinearLayer.get_weight_norm
    with norme_dora_sure():
        assert DoraLinearLayer.get_weight_norm is not avant
    assert DoraLinearLayer.get_weight_norm is avant
    modele = _modele_dora()
    assert not bool(torch.isfinite(modele.merge_and_unload().proj.weight).all())


def _modele_dora_entraine() -> torch.nn.Module:
    """Adaptateur « entraîné » simulé : `lora_B` et magnitude non triviaux (valeurs aléatoires).

    Comme sur l'adaptateur réel 1f18 : ligne morte avec `lora_B` nul et magnitude non nulle
    (norme de la base nf4 à l'initialisation)."""
    torch.manual_seed(1)
    modele = _modele_dora()
    with torch.no_grad():
        for nom, param in modele.named_parameters():
            if "lora_B" in nom:
                param.normal_(0.0, 0.5)
                param[2].zero_()
            elif "lora_magnitude_vector" in nom:
                param.mul_(1.0 + 0.1 * torch.rand_like(param))
                param[2] = 0.01
    return modele


def test_fusion_dora_lignes_vivantes_egales_au_forward_non_fusionne() -> None:
    import copy

    modele = _modele_dora_entraine().eval()
    entree = torch.randn(5, 8)
    with torch.no_grad():
        attendu = modele.base_model.model.proj(entree)
    sans_garde = copy.deepcopy(modele).merge_and_unload().proj.weight
    with norme_dora_sure():
        fusionne = modele.merge_and_unload()
    vivantes = [i for i in range(6) if i != 2]
    with torch.no_grad():
        obtenu = fusionne.proj(entree)
    assert torch.allclose(obtenu[:, vivantes], attendu[:, vivantes], atol=1e-5)
    # La garde ne touche pas les lignes de norme non nulle, et la ligne morte reste nulle.
    assert torch.equal(fusionne.proj.weight[vivantes], sans_garde[vivantes])
    assert float(fusionne.proj.weight[2].abs().max()) == 0.0
