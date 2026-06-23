document.addEventListener("DOMContentLoaded", function () {
  const mensagemEditor = document.getElementById("mensagem");
  const salvarModeloBtn = document.querySelector(".salvar-modelo");
  const gerenciarModelosBtn = document.querySelector(".gerenciar-modelos");
  const templateSelector = document.getElementById("template-selector");
  const modalModelos = document.getElementById("modal-modelos");
  const listaModelos = modalModelos.querySelector(".lista-modelos");
  const fecharModalBtns = document.querySelectorAll(".close-modal");

  // =============== AJUSTE NO EDITOR ===============
  // Transformar textarea em contenteditable
  const editableDiv = document.createElement("div");
  editableDiv.id = "editor";
  editableDiv.contentEditable = "true";
  editableDiv.classList.add("editor-box");
  editableDiv.style.minHeight = "100px";
  editableDiv.style.border = "1px solid #ccc";
  editableDiv.style.padding = "8px";
  editableDiv.style.borderRadius = "4px";

  mensagemEditor.style.display = "none"; // esconde o textarea
  mensagemEditor.parentNode.insertBefore(editableDiv, mensagemEditor);

  // Função para sincronizar conteúdo
  function syncMensagem() {
    mensagemEditor.value = editableDiv.innerHTML;
  }

  // Sincronizar sempre que digitar
  editableDiv.addEventListener("input", syncMensagem);

  // =============== FORMATOS (B e I) ===============
  document.querySelectorAll(".format-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const format = btn.dataset.format;
      editableDiv.focus();
      document.execCommand(format, false, null);
      syncMensagem();
    });
  });

  // =============== MODELOS ===============
  async function carregarModelos() {
    try {
      const resp = await fetch("/modelos/");
      const modelos = await resp.json();
      templateSelector.innerHTML = '<option value="">selecionar modelo</option>';
      listaModelos.innerHTML = "";

      modelos.forEach((m) => {
        // select
        const opt = document.createElement("option");
        opt.value = m.conteudo;
        opt.textContent = m.nome;
        templateSelector.appendChild(opt);

        // lista modal
        const item = document.createElement("div");
        item.classList.add("modelo-item");
        item.innerHTML = `
          <strong>${m.nome}</strong>
          <p>${m.conteudo}</p>
        `;
        listaModelos.appendChild(item);
      });
    } catch (e) {
      console.error("Erro ao carregar modelos:", e);
    }
  }

  // aplicar modelo selecionado
  templateSelector.addEventListener("change", () => {
    const conteudo = templateSelector.value;
    if (conteudo) {
      editableDiv.innerHTML = conteudo;
      syncMensagem();
    }
  });

  // salvar modelo
  salvarModeloBtn.addEventListener("click", async () => {
    const nome = prompt("Nome do modelo:");
    const conteudo = editableDiv.innerHTML.trim();
    if (!nome || !conteudo) return alert("Preencha nome e mensagem!");

    const resp = await fetch("/modelos/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nome, conteudo }),
    });
    const data = await resp.json();
    if (data.status === "ok") {
      alert("Modelo salvo!");
      carregarModelos();
    } else {
      alert("Erro ao salvar modelo");
    }
  });

  // gerenciar modelos (abrir modal)
  gerenciarModelosBtn.addEventListener("click", () => {
    modalModelos.style.display = "block";
    carregarModelos();
  });

  // fechar modais
  fecharModalBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      btn.closest(".modal").style.display = "none";
    });
  });

  // carregar modelos no início
  carregarModelos();
});
