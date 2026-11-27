(() => {
  "use strict";

  const state = {
    view: "chat",
    runtime: null,
    announcements: [],
    coachRoster: [],
    drafts: [],
    demoScenarios: [],
    messages: [],
    history: [],
    isSending: false,
    lastFailedText: "",
    activeMessageId: null,
    activeCitationCode: null,
    activeTrace: null,
    activeCitation: null,
    inspectorOpen: false,
    lastFocusedBeforeDrawer: null,
    msgSeq: 0,
    queueFilter: "all",
    highlightedDraftId: null,
    busyDraftIds: new Set(),
    isResettingQueue: false,
    kbFilter: "active",
    kbQuery: "",
    dataNotice: "",
  };

  const els = {
    navRail: document.getElementById("navRail"),
    mainWorkspace: document.getElementById("mainWorkspace"),
    openRailBtn: document.getElementById("openRailBtn"),
    closeRailBtn: document.getElementById("closeRailBtn"),
    inspectorPanel: document.getElementById("inspectorPanel"),
    openInspectorBtn: document.getElementById("openInspectorBtn"),
    closeInspectorBtn: document.getElementById("closeInspectorBtn"),
    drawerBackdrop: document.getElementById("drawerBackdrop"),
    navButtons: Array.from(document.querySelectorAll(".nav-item")),
    pendingBadge: document.getElementById("pendingBadge"),
    scenarioList: document.getElementById("scenarioList"),
    starterChips: document.getElementById("starterChips"),
    runtimeDot: document.getElementById("runtimeDot"),
    runtimeModeText: document.getElementById("runtimeModeText"),
    newSessionBtn: document.getElementById("newSessionBtn"),
    topbarTitle: document.getElementById("topbarTitle"),
    viewChat: document.getElementById("viewChat"),
    viewQueue: document.getElementById("viewQueue"),
    viewKnowledge: document.getElementById("viewKnowledge"),
    emptyState: document.getElementById("emptyState"),
    chatScroll: document.getElementById("chatScroll"),
    messageStream: document.getElementById("messageStream"),
    composerForm: document.getElementById("composerForm"),
    questionInput: document.getElementById("questionInput"),
    sendBtn: document.getElementById("sendBtn"),
    composerError: document.getElementById("composerError"),
    composerErrorText: document.getElementById("composerErrorText"),
    retryBtn: document.getElementById("retryBtn"),
    queueFilters: document.getElementById("queueFilters"),
    queueList: document.getElementById("queueList"),
    resetQueueBtn: document.getElementById("resetQueueBtn"),
    queueDataNotice: document.getElementById("queueDataNotice"),
    queueError: document.getElementById("queueError"),
    queueErrorText: document.getElementById("queueErrorText"),
    dismissQueueErrorBtn: document.getElementById("dismissQueueErrorBtn"),
    knowledgeSearch: document.getElementById("knowledgeSearch"),
    knowledgeFilters: document.getElementById("knowledgeFilters"),
    kbDataNotice: document.getElementById("kbDataNotice"),
    knowledgeContainer: document.getElementById("knowledgeContainer"),
    traceSummary: document.getElementById("traceSummary"),
    traceEvents: document.getElementById("traceEvents"),
    sourcePreview: document.getElementById("sourcePreview"),
  };

  const VIEW_TITLES = {
    chat: "Hỏi đáp buổi Lab",
    queue: "Duyệt chuyển Coach",
    knowledge: "Thông báo & Ca trực",
  };

  const STATUS_META = {
    pending_approval: { label: "Chờ duyệt", cls: "status-pill--warn" },
    approved: { label: "Đã duyệt", cls: "status-pill--ok" },
    needs_info: { label: "Cần bổ sung", cls: "status-pill--accent" },
    rejected: { label: "Từ chối", cls: "status-pill--danger" },
  };

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = text;
    return node;
  }

  function closeDrawers() {
    const wasOpen =
      els.navRail.classList.contains("is-open") || els.inspectorPanel.classList.contains("is-open");
    state.inspectorOpen = false;
    els.navRail.inert = false;
    els.mainWorkspace.inert = false;
    els.inspectorPanel.inert = false;
    els.navRail.classList.remove("is-open");
    els.inspectorPanel.classList.remove("is-open");
    els.inspectorPanel.setAttribute("aria-hidden", "true");
    els.drawerBackdrop.classList.remove("is-visible");
    els.openRailBtn.setAttribute("aria-expanded", "false");
    els.openInspectorBtn.setAttribute("aria-expanded", "false");
    syncCiteSelection();
    if (wasOpen && state.lastFocusedBeforeDrawer && typeof state.lastFocusedBeforeDrawer.focus === "function") {
      state.lastFocusedBeforeDrawer.focus();
      state.lastFocusedBeforeDrawer = null;
    }
  }

  function openRail() {
    state.lastFocusedBeforeDrawer = document.activeElement;
    state.inspectorOpen = false;
    els.inspectorPanel.classList.remove("is-open");
    els.inspectorPanel.setAttribute("aria-hidden", "true");
    els.openInspectorBtn.setAttribute("aria-expanded", "false");
    els.navRail.inert = false;
    els.mainWorkspace.inert = true;
    els.inspectorPanel.inert = true;
    els.navRail.classList.add("is-open");
    els.drawerBackdrop.classList.add("is-visible");
    els.openRailBtn.setAttribute("aria-expanded", "true");
    syncCiteSelection();
    els.closeRailBtn.focus();
  }

  function openInspector(triggerEl = null) {
    state.lastFocusedBeforeDrawer = triggerEl || document.activeElement;
    state.inspectorOpen = true;
    els.navRail.classList.remove("is-open");
    els.openRailBtn.setAttribute("aria-expanded", "false");
    els.inspectorPanel.inert = false;
    els.mainWorkspace.inert = true;
    els.navRail.inert = true;
    els.inspectorPanel.classList.add("is-open");
    els.inspectorPanel.setAttribute("aria-hidden", "false");
    els.drawerBackdrop.classList.add("is-visible");
    els.openInspectorBtn.setAttribute("aria-expanded", "true");
    syncCiteSelection();
    els.closeInspectorBtn.focus();
  }

  function switchView(viewName) {
    state.view = viewName;
    els.navButtons.forEach((btn) => {
      const active = btn.dataset.view === viewName;
      btn.classList.toggle("is-active", active);
      if (active) {
        btn.setAttribute("aria-current", "page");
      } else {
        btn.removeAttribute("aria-current");
      }
    });

    const panes = { chat: els.viewChat, queue: els.viewQueue, knowledge: els.viewKnowledge };
    Object.entries(panes).forEach(([key, pane]) => {
      const show = key === viewName;
      pane.hidden = !show;
      pane.classList.toggle("is-active", show);
    });

    els.topbarTitle.textContent = VIEW_TITLES[viewName] || VIEW_TITLES.chat;
    if (viewName === "queue") renderQueue();
    if (viewName === "knowledge") renderKnowledge();
    closeDrawers();
  }

  function appendFormattedInline(parent, text) {
    const tokenRegex = /(\*\*[^*]+\*\*|`[^`]+`)/g;
    let lastIndex = 0;
    let match;
    while ((match = tokenRegex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        parent.appendChild(document.createTextNode(text.slice(lastIndex, match.index)));
      }
      const chunk = match[0];
      if (chunk.startsWith("**") && chunk.endsWith("**")) {
        const strong = document.createElement("strong");
        strong.textContent = chunk.slice(2, -2);
        parent.appendChild(strong);
      } else if (chunk.startsWith("`") && chunk.endsWith("`")) {
        const code = document.createElement("code");
        code.textContent = chunk.slice(1, -1);
        parent.appendChild(code);
      }
      lastIndex = match.index + chunk.length;
    }
    if (lastIndex < text.length) {
      parent.appendChild(document.createTextNode(text.slice(lastIndex)));
    }
  }

  function renderRichText(text) {
    const container = el("div", "reply-body");
    const lines = String(text || "").split("\n");
    let currentList = null;

    lines.forEach((rawLine) => {
      const line = rawLine.trim();
      if (!line) {
        currentList = null;
        return;
      }
      if (line.startsWith("- ")) {
        if (!currentList) {
          currentList = document.createElement("ul");
          container.appendChild(currentList);
        }
        const li = document.createElement("li");
        appendFormattedInline(li, line.slice(2).trim());
        currentList.appendChild(li);
      } else {
        currentList = null;
        const p = document.createElement("p");
        appendFormattedInline(p, line);
        container.appendChild(p);
      }
    });
    return container;
  }

  function renderPendingBadge() {
    const pendingCount = state.drafts.filter((d) => d.status === "pending_approval").length;
    els.pendingBadge.textContent = String(pendingCount);
    els.pendingBadge.hidden = pendingCount === 0;
  }

  function renderScenarios() {
    els.scenarioList.replaceChildren();
    state.demoScenarios.slice(0, 4).forEach((sc) => {
      const btn = el("button", "scenario-btn", sc.label);
      btn.type = "button";
      btn.addEventListener("click", () => {
        switchView("chat");
        submitQuestion(sc.prompt);
      });
      els.scenarioList.appendChild(btn);
    });

    els.starterChips.replaceChildren();
    state.demoScenarios.slice(0, 4).forEach((sc) => {
      const chip = el("button", "starter-btn", sc.label);
      chip.type = "button";
      chip.addEventListener("click", () => submitQuestion(sc.prompt));
      els.starterChips.appendChild(chip);
    });
  }

  function renderRuntime() {
    if (!state.runtime) return;
    if (state.runtime.is_fake_mode) {
      els.runtimeDot.classList.remove("is-live");
      els.runtimeModeText.textContent = "Dữ liệu mẫu A2 · ngoại tuyến (fake)";
    } else {
      els.runtimeDot.classList.add("is-live");
      els.runtimeModeText.textContent = `Dữ liệu mẫu A2 · ${state.runtime.model_name}`;
    }
    if (state.dataNotice) {
      els.queueDataNotice.textContent = state.dataNotice;
      els.queueDataNotice.hidden = false;
      els.kbDataNotice.textContent = state.dataNotice;
      els.kbDataNotice.hidden = false;
    }
  }

  function renderChatStream() {
    els.emptyState.hidden = state.messages.length > 0 || state.isSending;
    els.messageStream.replaceChildren();

    state.messages.forEach((msg) => {
      if (msg.role === "user") {
        els.messageStream.appendChild(el("div", "msg-user", msg.content));
        return;
      }

      const data = msg.payload;
      const summary = msg.trace?.summary || {};
      const card = el("article", `msg-assistant ${msg.isNew ? "is-entering" : ""}`);
      msg.isNew = false;

      card.appendChild(renderRichText(data.output));

      // Gợi ý làm rõ nhanh (Lớp 2)
      if (Array.isArray(data.clarifying_options) && data.clarifying_options.length) {
        const actions = el("div", "clarify-actions");
        data.clarifying_options.forEach((opt) => {
          const optBtn = el("button", "chip-btn", opt);
          optBtn.type = "button";
          optBtn.addEventListener("click", () => submitQuestion(opt));
          actions.appendChild(optBtn);
        });
        card.appendChild(actions);
      }

      // Khối nháp chuyển Coach gọn nhẹ
      if (data.draft_handoff) {
        const d = data.draft_handoff;
        const bar = el("div", "draft-bar");
        const txt = el("div", "draft-bar-text");
        const strong = document.createElement("strong");
        strong.textContent = `Bản nháp ${d.draft_id}`;
        txt.appendChild(strong);
        txt.appendChild(
          document.createTextNode(` · ${d.coach_role} (${d.channel}) — đang chờ điều phối duyệt`)
        );
        bar.appendChild(txt);

        const openQueueBtn = el("button", "btn-secondary", "Xem & duyệt");
        openQueueBtn.type = "button";
        openQueueBtn.addEventListener("click", () => {
          state.highlightedDraftId = d.draft_id;
          state.queueFilter = "all";
          switchView("queue");
        });
        bar.appendChild(openQueueBtn);
        card.appendChild(bar);
      }

      // Chân thẻ gọn: trích dẫn nguồn + link mở Trace
      const hasCites = Array.isArray(data.citations) && data.citations.length > 0;
      const foot = el("div", "reply-foot");
      const citeWrap = el("div", "citation-links");
      if (hasCites) {
        data.citations.forEach((cite) => {
          const isExpired = cite.status === "expired";
          const isSelectedCite =
            state.inspectorOpen &&
            state.activeMessageId === msg.id &&
            state.activeCitationCode === cite.code;
          const btn = el(
            "button",
            `cite-link ${isExpired ? "cite-link--expired" : ""} ${isSelectedCite ? "is-selected" : ""}`
          );
          btn.type = "button";
          btn.dataset.msgId = msg.id;
          btn.setAttribute("aria-pressed", isSelectedCite ? "true" : "false");
          btn.appendChild(el("span", "cite-code", cite.code));
          btn.appendChild(document.createTextNode(isExpired ? "Hết hiệu lực" : cite.title));
          btn.addEventListener("click", (e) => {
            state.activeMessageId = msg.id;
            state.activeCitationCode = cite.code;
            state.activeCitation = cite;
            state.activeTrace = { result: data, trace: msg.trace };
            renderInspector(true);
            openInspector(e.currentTarget);
            syncCiteSelection();
          });
          citeWrap.appendChild(btn);
        });
      }
      foot.appendChild(citeWrap);

      const traceBtn = el(
        "button",
        "trace-link-btn",
        `Trace (${summary.tool_calls ?? 0} tool · ${summary.tokens_in ?? 0}/${summary.tokens_out ?? 0} tok)`
      );
      traceBtn.type = "button";
      traceBtn.addEventListener("click", (e) => {
        state.activeMessageId = msg.id;
        state.activeTrace = { result: data, trace: msg.trace };
        state.activeCitation = data.citations?.[0] || null;
        state.activeCitationCode = state.activeCitation ? state.activeCitation.code : null;
        renderInspector(Boolean(state.activeCitation));
        openInspector(e.currentTarget);
        syncCiteSelection();
      });
      foot.appendChild(traceBtn);
      card.appendChild(foot);

      els.messageStream.appendChild(card);
    });

    if (state.isSending) {
      const skel = el("div", "skeleton-msg");
      skel.setAttribute("aria-label", "Đang tra cứu");
      const l1 = el("div", "skel-bar");
      l1.style.width = "72%";
      const l2 = el("div", "skel-bar");
      l2.style.width = "88%";
      const l3 = el("div", "skel-bar");
      l3.style.width = "48%";
      skel.append(l1, l2, l3);
      els.messageStream.appendChild(skel);
    }

    requestAnimationFrame(() => {
      els.chatScroll.scrollTop = els.chatScroll.scrollHeight;
    });
  }

  function syncCiteSelection() {
    // Cập nhật class active mà không dựng lại DOM chat (giữ nguyên focus nút đã bấm)
    const buttons = els.messageStream.querySelectorAll(".cite-link");
    buttons.forEach((btn) => {
      const code = btn.querySelector(".cite-code")?.textContent || "";
      const active = Boolean(
        state.inspectorOpen &&
          state.activeMessageId &&
          btn.dataset.msgId === state.activeMessageId &&
          state.activeCitationCode &&
          code === state.activeCitationCode
      );
      btn.classList.toggle("is-selected", active);
      btn.setAttribute("aria-pressed", active ? "true" : "false");
    });
  }

  function renderInspector(pulseSource = false) {
    const active = state.activeTrace;
    if (!active) {
      els.traceSummary.replaceChildren(
        metricRow("Quyết định", "—"),
        metricRow("Model", state.runtime?.model_name || "fake"),
        metricRow("Công cụ / Token", "0 · 0/0")
      );
      els.traceEvents.replaceChildren(el("p", "empty-muted", "Chưa có sự kiện nào."));
    } else {
      const s = active.trace?.summary || {};
      const r = active.result || {};
      const events = active.trace?.events || [];
      const totalLatency = events.length ? events[events.length - 1].t : 0;

      els.traceSummary.replaceChildren(
        metricRow("Quyết định", r.decision || "—"),
        metricRow("Model", (s.models && s.models.join(", ")) || (r.model_mode || "guard")),
        metricRow("Công cụ / Token", `${s.tool_calls ?? 0} · ${s.tokens_in ?? 0}/${s.tokens_out ?? 0} (${totalLatency}s)`)
      );

      els.traceEvents.replaceChildren();
      if (!events.length) {
        els.traceEvents.appendChild(el("p", "empty-muted", "Không có sự kiện tool/model nào."));
      } else {
        events.forEach((ev) => {
          const box = el("div", "trace-event");
          const top = el("div", "trace-event-head");
          const label = ev.kind === "note" ? "note" : `${ev.kind}: ${ev.name || ""}`;
          top.appendChild(el("span", "trace-event-kind", label));
          top.appendChild(el("span", "trace-event-time", `${ev.t ?? 0}s`));
          box.appendChild(top);

          const detailText =
            ev.kind === "note"
              ? ev.text
              : ev.kind === "model"
              ? `model=${ev.model} · in=${ev.tokens_in} · out=${ev.tokens_out}`
              : ev.error
              ? `lỗi: ${ev.error}`
              : `trễ ${ev.latency_s ?? 0}s`;
          box.appendChild(el("div", "trace-event-detail", detailText));
          els.traceEvents.appendChild(box);
        });
      }
    }

    const cite = state.activeCitation;
    els.sourcePreview.classList.remove("is-pulsing");
    els.sourcePreview.replaceChildren();
    if (!cite) {
      els.sourcePreview.appendChild(
        el("p", "empty-muted", "Chọn một trích dẫn trong câu trả lời để xem nguyên văn thông báo.")
      );
    } else {
      els.sourcePreview.appendChild(el("h4", "", cite.title));
      const badgeCls = cite.status === "expired" ? "status-pill--danger" : "status-pill--ok";
      const badgeLabel = cite.status === "expired" ? "Hết hiệu lực" : `Hiệu lực ${cite.effective_date}`;
      els.sourcePreview.appendChild(el("span", `status-pill ${badgeCls}`, `${cite.code} · ${badgeLabel}`));
      els.sourcePreview.appendChild(el("p", "", cite.summary));
      if (Array.isArray(cite.details) && cite.details.length) {
        const ul = document.createElement("ul");
        cite.details.forEach((d) => ul.appendChild(el("li", "", d)));
        els.sourcePreview.appendChild(ul);
      }
      els.sourcePreview.appendChild(el("p", "empty-muted", cite.source_ref));
      if (pulseSource) {
        void els.sourcePreview.offsetWidth;
        els.sourcePreview.classList.add("is-pulsing");
      }
    }
  }

  function metricRow(label, value) {
    const row = el("div", "metric-row");
    row.appendChild(el("span", "", label));
    row.appendChild(el("span", "mono-val", value));
    return row;
  }

  function renderQueue() {
    const counts = { all: state.drafts.length, pending_approval: 0, approved: 0, needs_info: 0, rejected: 0 };
    state.drafts.forEach((d) => {
      if (counts[d.status] !== undefined) counts[d.status] += 1;
    });

    const baseLabels = {
      all: "Tất cả",
      pending_approval: "Chờ duyệt",
      approved: "Đã duyệt",
      needs_info: "Cần bổ sung",
      rejected: "Từ chối",
    };

    Array.from(els.queueFilters.querySelectorAll(".filter-pill")).forEach((btn) => {
      const key = btn.dataset.filter;
      const isSelected = key === state.queueFilter;
      btn.textContent = `${baseLabels[key]} (${counts[key] ?? 0})`;
      btn.classList.toggle("is-active", isSelected);
      btn.setAttribute("aria-pressed", isSelected ? "true" : "false");
    });

    const filtered = state.drafts.filter(
      (d) => state.queueFilter === "all" || d.status === state.queueFilter
    );
    els.queueList.replaceChildren();

    if (!filtered.length) {
      els.queueList.appendChild(
        el("div", "empty-state-box", "Không có bản nháp nào ở trạng thái này.")
      );
      return;
    }

    filtered.forEach((d) => {
      const card = el(
        "article",
        `queue-card ${state.highlightedDraftId === d.draft_id ? "is-highlighted" : ""}`
      );
      const head = el("div", "queue-card-head");
      const titleLine = el("div", "queue-title-line");
      titleLine.appendChild(el("span", "mono-val", d.draft_id));
      titleLine.appendChild(document.createTextNode(`${d.coach_role || d.coach_id} · ${d.channel || ""}`));
      const st = STATUS_META[d.status] || { label: d.status, cls: "" };
      titleLine.appendChild(el("span", `status-pill ${st.cls}`, st.label));
      head.appendChild(titleLine);
      head.appendChild(el("span", "mono-val empty-muted", d.created_at || ""));
      card.appendChild(head);

      card.appendChild(el("p", "queue-question", d.question));

      const msgWrap = el("div");
      const msgLabel = el("label", "field-label", "Nội dung chuyển Coach");
      const msgId = `draft-msg-${d.draft_id}`;
      msgLabel.setAttribute("for", msgId);
      const textarea = el("textarea", "draft-textarea");
      textarea.id = msgId;
      textarea.rows = 2;
      textarea.value = d.draft_message || "";
      msgWrap.append(msgLabel, textarea);
      card.appendChild(msgWrap);

      const noteWrap = el("div");
      const noteLabel = el("label", "field-label", "Ghi chú duyệt");
      const noteId = `draft-note-${d.draft_id}`;
      noteLabel.setAttribute("for", noteId);
      const noteInput = el("input", "note-input");
      noteInput.id = noteId;
      noteInput.type = "text";
      noteInput.value = d.coordinator_note || "";
      noteInput.placeholder = "Thêm ghi chú cho coach hoặc học viên (tuỳ chọn)...";
      noteWrap.append(noteLabel, noteInput);
      card.appendChild(noteWrap);

      const isBusy = state.busyDraftIds.has(d.draft_id) || state.isResettingQueue;
      textarea.disabled = isBusy;
      noteInput.disabled = isBusy;

      const actions = el("div", "queue-actions");
      if (d.status === "pending_approval" || d.status === "needs_info") {
        const approveBtn = el("button", "btn-primary", isBusy ? "Đang lưu..." : "Duyệt gửi");
        approveBtn.type = "button";
        approveBtn.disabled = isBusy;
        approveBtn.addEventListener("click", () =>
          actOnDraft(d.draft_id, "approve", noteInput.value, textarea.value)
        );

        const infoBtn = el("button", "btn-secondary", "Hỏi thêm");
        infoBtn.type = "button";
        infoBtn.disabled = isBusy;
        infoBtn.addEventListener("click", () =>
          actOnDraft(d.draft_id, "request_info", noteInput.value, textarea.value)
        );

        const rejectBtn = el("button", "btn-danger-outline", "Từ chối");
        rejectBtn.type = "button";
        rejectBtn.disabled = isBusy;
        rejectBtn.addEventListener("click", () =>
          actOnDraft(d.draft_id, "reject", noteInput.value, textarea.value)
        );

        actions.append(approveBtn, infoBtn, rejectBtn);
      } else {
        const reopenBtn = el("button", "btn-secondary", isBusy ? "Đang lưu..." : "Mở lại");
        reopenBtn.type = "button";
        reopenBtn.disabled = isBusy;
        reopenBtn.addEventListener("click", () =>
          actOnDraft(d.draft_id, "reopen", noteInput.value, textarea.value)
        );
        actions.appendChild(reopenBtn);
        if (d.reviewed_at) {
          actions.appendChild(el("span", "empty-muted", `Cập nhật ${d.reviewed_at}`));
        }
      }

      card.appendChild(actions);
      els.queueList.appendChild(card);
    });
  }

  function renderKnowledge() {
    Array.from(els.knowledgeFilters.querySelectorAll(".filter-pill")).forEach((btn) => {
      const isSelected = btn.dataset.kbFilter === state.kbFilter;
      btn.classList.toggle("is-active", isSelected);
      btn.setAttribute("aria-pressed", isSelected ? "true" : "false");
    });

    const q = state.kbQuery.trim().toLowerCase();
    els.knowledgeContainer.replaceChildren();

    if (state.kbFilter === "roster") {
      const coaches = state.coachRoster.filter((c) => {
        if (!q) return true;
        return [c.coach_id, c.role_title, c.shift, c.channel, ...(c.topics || [])].join(" ").toLowerCase().includes(q);
      });
      if (coaches.length) {
        const wrap = el("div", "roster-table-wrap");
        const table = el("table", "roster-table");
        const thead = document.createElement("thead");
        const hr = document.createElement("tr");
        ["Đầu mối", "Ca trực", "Kênh & SLA"].forEach((h) => hr.appendChild(el("th", "", h)));
        thead.appendChild(hr);
        table.appendChild(thead);

        const tbody = document.createElement("tbody");
        coaches.forEach((c) => {
          const tr = document.createElement("tr");
          tr.appendChild(el("td", "", c.role_title));
          tr.appendChild(el("td", "", c.shift));
          tr.appendChild(el("td", "", `${c.channel} · ${c.sla}`));
          tbody.appendChild(tr);
        });
        table.appendChild(tbody);
        wrap.appendChild(table);
        els.knowledgeContainer.appendChild(wrap);
      }
    } else {
      const items = state.announcements.filter((a) => {
        if (a.status !== state.kbFilter) return false;
        if (!q) return true;
        return [a.code, a.title, a.summary, a.source_ref, ...(a.details || [])].join(" ").toLowerCase().includes(q);
      });

      items.forEach((a) => {
        const item = el("article", "kb-item");
        item.appendChild(el("h3", "kb-title", a.title));
        const meta = el("div", "kb-meta");
        meta.appendChild(el("span", "mono-val", a.code));
        meta.appendChild(document.createTextNode(a.status === "expired" ? "Hết hiệu lực" : `Cập nhật ${a.effective_date}`));
        meta.appendChild(document.createTextNode(`· ${a.source_ref}`));
        item.appendChild(meta);
        item.appendChild(el("p", "kb-summary", a.summary));

        if (Array.isArray(a.details) && a.details.length) {
          const ul = el("ul", "kb-details");
          a.details.forEach((line) => ul.appendChild(el("li", "", line)));
          item.appendChild(ul);
        }
        els.knowledgeContainer.appendChild(item);
      });
    }

    if (!els.knowledgeContainer.children.length) {
      els.knowledgeContainer.appendChild(
        el("div", "empty-state-box", "Không có mục nào phù hợp.")
      );
    }
  }

  async function submitQuestion(text) {
    const trimmed = String(text || "").trim();
    if (!trimmed) {
      showError("Vui lòng nhập câu hỏi trước khi gửi.");
      return;
    }
    if (state.isSending) return;

    hideError();
    state.isSending = true;
    state.lastFailedText = "";
    els.sendBtn.disabled = true;
    els.sendBtn.textContent = "Đang gửi...";

    state.messages.push({ role: "user", content: trimmed });
    const historyToSend = state.history.slice(-6);
    els.questionInput.value = "";
    autoResizeInput();
    renderChatStream();

    try {
      const resp = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: trimmed, history: historyToSend }),
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || `HTTP ${resp.status}`);

      const payload = data.result;
      const msgId = `msg-${++state.msgSeq}`;
      state.messages.push({ id: msgId, role: "assistant", payload, trace: data.trace, isNew: true });
      state.history.push({ role: "user", content: trimmed });
      state.history.push({ role: "assistant", content: payload.output, decision: payload.decision });
      if (Array.isArray(data.drafts)) state.drafts = data.drafts;

      state.activeMessageId = msgId;
      state.activeCitation = payload.citations?.[0] || null;
      state.activeCitationCode = state.activeCitation ? state.activeCitation.code : null;
      state.activeTrace = { result: payload, trace: data.trace };
      renderPendingBadge();
      renderInspector(false);
    } catch (err) {
      state.lastFailedText = trimmed;
      state.messages.pop();
      showError(`Không thể xử lý câu hỏi: ${err.message}`);
    } finally {
      state.isSending = false;
      els.sendBtn.disabled = false;
      els.sendBtn.textContent = "Gửi";
      renderChatStream();
    }
  }

  async function actOnDraft(draftId, action, note, draftMessage) {
    if (state.busyDraftIds.has(draftId) || state.isResettingQueue) return;
    els.queueError.hidden = true;
    state.busyDraftIds.add(draftId);
    renderQueue();
    try {
      const resp = await fetch(`/api/drafts/${encodeURIComponent(draftId)}/action`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, note, draft_message: draftMessage }),
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || `HTTP ${resp.status}`);
      if (Array.isArray(data.queue)) state.drafts = data.queue;
      state.highlightedDraftId = draftId;
      renderPendingBadge();
    } catch (err) {
      els.queueErrorText.textContent = `Không cập nhật được bản nháp: ${err.message}`;
      els.queueError.hidden = false;
    } finally {
      state.busyDraftIds.delete(draftId);
      renderQueue();
    }
  }

  async function resetDemoQueue() {
    if (state.isResettingQueue) return;
    els.queueError.hidden = true;
    state.isResettingQueue = true;
    els.resetQueueBtn.disabled = true;
    els.resetQueueBtn.textContent = "Đang khôi phục...";
    renderQueue();
    try {
      const resp = await fetch("/api/drafts/reset", { method: "POST" });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || `HTTP ${resp.status}`);
      if (Array.isArray(data.drafts)) {
        state.drafts = data.drafts;
        state.highlightedDraftId = null;
        renderPendingBadge();
      }
    } catch (err) {
      els.queueErrorText.textContent = `Không khôi phục được mẫu: ${err.message}`;
      els.queueError.hidden = false;
    } finally {
      state.isResettingQueue = false;
      els.resetQueueBtn.disabled = false;
      els.resetQueueBtn.textContent = "Khôi phục mẫu";
      renderQueue();
    }
  }

  function showError(msg) {
    els.composerErrorText.textContent = msg;
    els.composerError.hidden = false;
  }

  function hideError() {
    els.composerError.hidden = true;
    els.composerErrorText.textContent = "";
  }

  function autoResizeInput() {
    const input = els.questionInput;
    input.style.height = "auto";
    const nextH = Math.min(input.scrollHeight, 150);
    input.style.height = `${nextH}px`;
    input.style.overflowY = input.scrollHeight > 150 ? "auto" : "hidden";
  }

  async function bootstrap() {
    try {
      const resp = await fetch("/api/bootstrap");
      const data = await resp.json();
      state.runtime = data.runtime;
      state.dataNotice = data.metadata?.note || "";
      state.announcements = data.announcements || [];
      state.coachRoster = data.coach_roster || [];
      state.drafts = data.drafts || [];
      state.demoScenarios = data.demo_scenarios || [];

      renderRuntime();
      renderPendingBadge();
      renderQueue();
      renderKnowledge();
      renderScenarios();
      renderInspector();
      renderChatStream();
      autoResizeInput();
    } catch (err) {
      showError(`Không tải được dữ liệu: ${err.message}`);
    }
  }

  els.openRailBtn.addEventListener("click", openRail);
  els.closeRailBtn.addEventListener("click", closeDrawers);
  els.openInspectorBtn.addEventListener("click", () => openInspector(els.openInspectorBtn));
  els.closeInspectorBtn.addEventListener("click", closeDrawers);
  els.drawerBackdrop.addEventListener("click", closeDrawers);

  els.navButtons.forEach((btn) => {
    btn.addEventListener("click", () => switchView(btn.dataset.view));
  });

  els.newSessionBtn.addEventListener("click", () => {
    state.messages = [];
    state.history = [];
    state.activeMessageId = null;
    state.activeCitationCode = null;
    state.activeTrace = null;
    state.activeCitation = null;
    hideError();
    switchView("chat");
    renderChatStream();
    renderInspector();
    els.questionInput.focus();
  });

  els.composerForm.addEventListener("submit", (e) => {
    e.preventDefault();
    submitQuestion(els.questionInput.value);
  });

  els.questionInput.addEventListener("input", () => {
    autoResizeInput();
    if (els.questionInput.value.trim()) hideError();
  });

  els.questionInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submitQuestion(els.questionInput.value);
    }
  });

  els.retryBtn.addEventListener("click", () => {
    if (state.lastFailedText) submitQuestion(state.lastFailedText);
  });

  els.queueFilters.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-filter]");
    if (!btn) return;
    state.queueFilter = btn.dataset.filter;
    renderQueue();
  });

  els.resetQueueBtn.addEventListener("click", resetDemoQueue);
  els.dismissQueueErrorBtn.addEventListener("click", () => {
    els.queueError.hidden = true;
  });

  els.knowledgeFilters.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-kb-filter]");
    if (!btn) return;
    state.kbFilter = btn.dataset.kbFilter;
    renderKnowledge();
  });

  els.knowledgeSearch.addEventListener("input", () => {
    state.kbQuery = els.knowledgeSearch.value;
    renderKnowledge();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeDrawers();
  });

  bootstrap();
})();
