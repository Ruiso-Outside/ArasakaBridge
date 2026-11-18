# ARASAKA BRIDGE

Programas Windows no **Zorin OS** com a cara da Arasaka, com foco no **Roblox Studio**.

O Bridge é uma central de controle em cima de ferramentas que já funcionam bem no Linux:

| Peça | Para que serve |
|---|---|
| **Wine** | Roda programas Windows (.exe / .msi) |
| **Winetricks** | Instala componentes que os programas pedem (Visual C++, .NET, fontes, DXVK) |
| **DXVK / VKD3D** | Converte DirectX para Vulkan, com mais desempenho em programas 3D |
| **Vinegar** (Flatpak) | Roda o **Roblox Studio** com as correções específicas que ele precisa |
| **Sober** (Flatpak, opcional) | Roda o Roblox Player (jogos), já que o anti-cheat dos jogos bloqueia o Wine |

## Abas do app

| Aba | O que tem |
|---|---|
| **01 Painel** | Verifica Wine, Winetricks, 32-bit, Flatpak, Vinegar e GPU/Vulkan. O que faltar tem um botão INSTALAR, que pede a senha numa janela gráfica |
| **02 Roblox Studio** | Instala, abre, atualiza, configura e encerra o Studio. Também abre as pastas de dados e de configuração do Vinegar |
| **03 Aplicativos** | Containers (um "mini Windows" isolado cada). Instale programas, rode .exe, adicione componentes e use as ferramentas (winecfg, regedit, gerenciador de tarefas, CMD). Duplo clique abre o programa; botão direito cria atalho no menu do Zorin e na área de trabalho |
| **04 Configurações** | Comando do Wine, esync/fsync, componentes padrão para novos containers, logs |

O terminal na parte de baixo mostra tudo o que está sendo executado. Os programas abertos continuam
rodando mesmo se você fechar o Bridge. A saída deles fica em `~/.local/share/arasaka-bridge/logs`.

## Instalar

```bash
tar xzf ArasakaBridge.tar.gz && cd ArasakaBridge
```

```bash
./install.sh
```

Rode **sem sudo**; ele pede a senha quando precisa. O instalador cuida de três coisas:
- dependências do sistema (Qt), Wine com 32-bit e Winetricks;
- o app num ambiente Python isolado (PySide6, cerca de 120 MB);
- Flatpak, Flathub e o Vinegar, além de associar `.exe` e `.msi` ao Bridge, para abrir com duplo clique.

| Opção | Efeito |
|---|---|
| `--sem-wine` | Não instala o Wine (use se já tiver o WineHQ, por exemplo) |
| `--sem-vinegar` | Não instala o Vinegar |
| `--nao-associar` | Não muda o programa padrão dos `.exe` |

## Roblox Studio: primeiro uso

1. Abra o **Arasaka Bridge** e vá em **02 Roblox Studio**, depois clique em **ABRIR ROBLOX STUDIO**.
   Também dá para clicar com o botão direito no ícone do menu e escolher *Abrir Roblox Studio*.
2. Na primeira vez, o Vinegar baixa o Studio e prepara o Wine. Isso leva alguns minutos.
3. No login, o Studio abre o navegador. Depois de entrar, ele volta sozinho para o Studio.
4. Se a tela ficar preta, piscar ou travar, clique em **CONFIGURAR VINEGAR** e troque o renderizador
   (D3D11 ou Vulkan). Confira também se a GPU tem driver Vulkan na aba **Painel**.

## Outros programas

1. Em **03 Aplicativos**, clique em **NOVO CONTAINER**. Deixe marcados os componentes recomendados.
2. Clique em **INSTALAR PROGRAMA** e escolha o instalador `.exe` ou `.msi`.
3. O programa aparece na lista. Com o botão direito, crie um atalho no menu do Zorin.

Dicas:
- Use um container por programa "chato" (que mexe muito no sistema). Se algo quebrar, é só excluir
  o container sem afetar os outros.
- Se o programa pedir .NET, Visual C++ ou DirectX, use **COMPONENTES** (Winetricks).
- Nem todo programa roda no Wine. Antes de instalar, pesquise o nome dele em
  [appdb.winehq.org](https://appdb.winehq.org).

## Linha de comando

```bash
arasaka-bridge                    # abre a interface
arasaka-bridge setup.exe          # pergunta em qual container executar
arasaka-bridge --studio           # abre o Roblox Studio direto
arasaka-bridge --launch SLUG ALVO # usado pelos atalhos do menu
```

## Desinstalar

```bash
./uninstall.sh
```

O comando acima remove só o app e mantém os containers. Para apagar também os containers, use
`./uninstall.sh --tudo`.

Arasaka é marca da CD PROJEKT RED, e a fonte cedge1 usa a licença FontStruct Non-Commercial; uso
pessoal de fã. Roblox é marca da Roblox Corporation. Vinegar e Sober são projetos da comunidade
VinegarHQ, e o Bridge só instala e abre os dois.
