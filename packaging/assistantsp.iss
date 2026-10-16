; Installateur de l'Assistant (story 12.13, FR-21, FR-22, NFR-6 ; Q2, Q3, Q4, Q6).
; Compilé par outils/construire_installateur.py, qui passe à ISCC :
;   /DVersionApp=<x.y.z>  /DDossierSource=<dist\AssistantSP>  /DDossierSortie=<dossier>
;   /DDecoupage=1            (seulement si le paquet dépasse 2 Go : DiskSpanning)
;   /DPackComplet=<chemin>   (variante « pack complet » : installateur autonome WebView2, Q2)
; Installation par utilisateur, sans droits administrateur, sans signature (Q4).

#ifndef VersionApp
  #define VersionApp "0.0.0"
#endif
#ifndef DossierSource
  #error DossierSource manquant : lancer outils/construire_installateur.py
#endif
#ifndef DossierSortie
  #define DossierSortie "."
#endif

#define NomApp "Assistant SP"
#define DossierDonnees "{localappdata}\AssistantSP"

[Setup]
; AppId stable : une nouvelle version s'installe par-dessus l'ancienne, données conservées (Q6).
AppId={{6F3A1C52-8B4E-4D7A-9C21-5E0B7D4A3F18}
AppName={#NomApp}
AppVersion={#VersionApp}
AppPublisher=Assistant SP
PrivilegesRequired=lowest
DefaultDirName={localappdata}\Programs\AssistantSP
DefaultGroupName={#NomApp}
; Trois écrans au plus : accueil, progression, fin (ni dossier, ni groupe, ni récapitulatif).
DisableDirPage=yes
DisableProgramGroupPage=yes
DisableReadyPage=yes
DisableWelcomePage=no
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir={#DossierSortie}
OutputBaseFilename=AssistantSP-Setup-{#VersionApp}
UninstallDisplayIcon={app}\AssistantSP.exe
; Les GGUF se compressent peu : compression rapide.
Compression=lzma2/fast
SolidCompression=no
#ifdef Decoupage
DiskSpanning=yes
DiskSliceSize=2000000000
#endif

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Files]
Source: "{#DossierSource}\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
#ifdef PackComplet
Source: "{#PackComplet}"; DestDir: "{tmp}"; DestName: "webview2-setup.exe"; Flags: deleteafterinstall; Check: not WebView2Installe
#endif

[Icons]
Name: "{autoprograms}\{#NomApp}"; Filename: "{app}\AssistantSP.exe"

[Run]
#ifdef PackComplet
Filename: "{tmp}\webview2-setup.exe"; Parameters: "/silent /install"; StatusMsg: "Installation du runtime WebView2..."; Check: not WebView2Installe
#endif
Filename: "{app}\AssistantSP.exe"; Description: "Lancer l'assistant"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
const
  GuidWebView2 = '{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}';
  CleWebView2 = 'EdgeUpdate\Clients\' + GuidWebView2;

function VersionValide(const Valeur: String): Boolean;
begin
  Result := (Valeur <> '') and (Valeur <> '0.0.0.0');
end;

{ Runtime WebView2 : valeur « pv » de la clé EdgeUpdate, machine (32 et 64 bits) ou utilisateur. }
function WebView2Installe: Boolean;
var
  Version: String;
begin
  Result :=
    (RegQueryStringValue(HKLM32, 'SOFTWARE\Microsoft\' + CleWebView2, 'pv', Version) and VersionValide(Version)) or
    (RegQueryStringValue(HKLM64, 'SOFTWARE\Microsoft\' + CleWebView2, 'pv', Version) and VersionValide(Version)) or
    (RegQueryStringValue(HKCU, 'Software\Microsoft\' + CleWebView2, 'pv', Version) and VersionValide(Version));
end;

function InitializeSetup: Boolean;
begin
  Result := True;
#ifndef PackComplet
  if not WebView2Installe then
  begin
    SuppressibleMsgBox(
      'Le composant Microsoft Edge WebView2 Runtime est absent de ce poste.' + #13#10 +
      'L''Assistant ne peut pas s''installer sans lui.' + #13#10#13#10 +
      'Demandez à votre service informatique (DSI) de l''installer, puis relancez cette installation.',
      mbError, MB_OK, IDOK);
    Result := False;
  end;
#endif
end;

{ Désinstallation : une seule question. « Non » supprime aussi les données (FR-22).
  Mode silencieux : données conservées, sauf /SupprimerDonnees=1. }
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  Supprimer: Boolean;
begin
  if CurUninstallStep <> usPostUninstall then Exit;
  Supprimer := ExpandConstant('{param:SupprimerDonnees|0}') = '1';
  if (not Supprimer) and (not UninstallSilent) then
    Supprimer := MsgBox('Conserver l''historique et les retours sur ce poste ?',
      mbConfirmation, MB_YESNO or MB_DEFBUTTON1) = IDNO;
  if Supprimer then
    DelTree(ExpandConstant('{#DossierDonnees}'), True, True, True);
end;
