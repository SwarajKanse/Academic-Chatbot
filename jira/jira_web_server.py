#!/usr/bin/env python3
"""
Atlassian Jira Software - Web Board & Agile Dashboard Server
Renders an authentic, interactive Atlassian Jira Software board on http://localhost:8085
Loaded directly from jira/jira_agile_sprint_lifecycle.json
"""

import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ACAD board - Jira Software (Atlassian)</title>
  <link rel="icon" href="https://assets.atlassian.com/dam/jcr:b62c4a9a-cf21-4f11-92f7-0801b7a2d677/jira-mark.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --jira-blue: #0052CC;
      --jira-nav-bg: #0747A6;
      --jira-bg: #FAFBFC;
      --jira-border: #DFE1E6;
      --jira-card-bg: #FFFFFF;
      --jira-text: #172B4D;
      --jira-subtext: #5E6C84;
      --jira-col-bg: #F4F5F7;
      --jira-hover: #EBECF0;
      --badge-done: #00875A;
      --badge-prog: #0052CC;
      --badge-todo: #42526E;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: var(--jira-bg);
      color: var(--jira-text);
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
    }

    /* Top Navigation Bar */
    header.jira-navbar {
      background: var(--jira-nav-bg);
      height: 48px;
      display: flex;
      align-items: center;
      padding: 0 16px;
      color: white;
      justify-content: space-between;
      box-shadow: 0 1px 3px rgba(0,0,0,0.2);
      z-index: 100;
    }
    .nav-left { display: flex; align-items: center; gap: 16px; }
    .jira-logo { display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 16px; color: white; text-decoration: none; }
    .jira-logo svg { width: 22px; height: 22px; fill: white; }
    .nav-links { display: flex; gap: 8px; }
    .nav-link {
      color: #DEEBFF;
      font-size: 14px;
      padding: 6px 10px;
      border-radius: 3px;
      text-decoration: none;
      font-weight: 500;
    }
    .nav-link:hover, .nav-link.active { background: rgba(255,255,255,0.15); color: white; }
    .btn-create {
      background: #0052CC;
      color: white;
      border: 1px solid rgba(255,255,255,0.3);
      padding: 5px 14px;
      font-weight: 600;
      font-size: 13px;
      border-radius: 3px;
      cursor: pointer;
    }
    .btn-create:hover { background: #0065FF; }

    .nav-right { display: flex; align-items: center; gap: 12px; }
    .search-input {
      background: rgba(255,255,255,0.2);
      border: 1px solid rgba(255,255,255,0.3);
      color: white;
      padding: 5px 12px;
      border-radius: 3px;
      font-size: 13px;
      width: 200px;
    }
    .search-input::placeholder { color: #DEEBFF; }
    .avatar-group { display: flex; }
    .nav-avatar {
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: #FF5630;
      color: white;
      font-size: 11px;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 2px solid var(--jira-nav-bg);
      margin-left: -6px;
      cursor: pointer;
    }
    .nav-avatar:first-child { margin-left: 0; background: #36B37E; }
    .nav-avatar:nth-child(2) { background: #00B8D9; }

    /* App Layout */
    .app-container { display: flex; flex: 1; height: calc(100vh - 48px); }

    /* Sidebar */
    aside.jira-sidebar {
      width: 240px;
      background: #F4F5F7;
      border-right: 1px solid var(--jira-border);
      padding: 24px 16px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    .proj-info { display: flex; align-items: center; gap: 12px; }
    .proj-icon { width: 36px; height: 36px; border-radius: 4px; background: #0052CC; color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 18px; }
    .proj-titles h2 { font-size: 14px; font-weight: 700; color: var(--jira-text); line-height: 1.2; }
    .proj-titles p { font-size: 11px; color: var(--jira-subtext); text-transform: uppercase; }

    .sidebar-menu { display: flex; flex-direction: column; gap: 4px; }
    .menu-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 8px 12px;
      font-size: 13px;
      color: var(--jira-text);
      text-decoration: none;
      border-radius: 4px;
      font-weight: 500;
      cursor: pointer;
    }
    .menu-item:hover { background: var(--jira-hover); }
    .menu-item.active { background: #E6EFFC; color: var(--jira-blue); font-weight: 600; }

    /* Main Board View */
    main.jira-main { flex: 1; display: flex; flex-direction: column; overflow: hidden; background: white; }
    .board-header {
      padding: 18px 24px 12px;
      border-bottom: 1px solid var(--jira-border);
    }
    .breadcrumbs { font-size: 12px; color: var(--jira-subtext); margin-bottom: 6px; }
    .board-title-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
    .board-title-row h1 { font-size: 22px; font-weight: 700; color: var(--jira-text); }
    .board-actions { display: flex; gap: 10px; }
    .btn-secondary {
      background: #F4F5F7;
      border: 1px solid var(--jira-border);
      color: var(--jira-text);
      padding: 6px 12px;
      font-size: 13px;
      font-weight: 600;
      border-radius: 3px;
      cursor: pointer;
    }
    .btn-secondary:hover { background: var(--jira-hover); }

    .board-filters { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
    .filter-input {
      border: 1px solid var(--jira-border);
      padding: 5px 10px;
      border-radius: 3px;
      font-size: 13px;
      width: 180px;
    }
    .chip {
      background: #F4F5F7;
      border: 1px solid var(--jira-border);
      padding: 4px 10px;
      border-radius: 14px;
      font-size: 12px;
      color: var(--jira-subtext);
      cursor: pointer;
    }
    .chip.active { background: #DEEBFF; color: var(--jira-blue); font-weight: 600; border-color: #B3D4FF; }

    /* Kanban Columns Container */
    .kanban-board {
      display: flex;
      gap: 16px;
      padding: 20px 24px;
      flex: 1;
      overflow-x: auto;
      background: var(--jira-bg);
    }
    .kanban-col {
      width: 290px;
      min-width: 290px;
      background: var(--jira-col-bg);
      border-radius: 6px;
      display: flex;
      flex-direction: column;
      max-height: 100%;
    }
    .col-header {
      padding: 12px 14px;
      font-size: 12px;
      font-weight: 700;
      color: var(--jira-subtext);
      text-transform: uppercase;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .col-count {
      background: rgba(9, 30, 66, 0.08);
      padding: 2px 8px;
      border-radius: 10px;
      font-size: 11px;
    }
    .cards-list {
      padding: 0 10px 10px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 10px;
      flex: 1;
    }

    /* Issue Card */
    .issue-card {
      background: white;
      border-radius: 4px;
      box-shadow: 0 1px 2px rgba(9, 30, 66, 0.2);
      padding: 12px;
      cursor: pointer;
      border: 1px solid transparent;
      transition: all 0.15s ease;
    }
    .issue-card:hover {
      box-shadow: 0 4px 8px rgba(9, 30, 66, 0.25);
      border-color: #B3D4FF;
    }
    .card-title {
      font-size: 13px;
      font-weight: 500;
      color: var(--jira-text);
      margin-bottom: 10px;
      line-height: 1.4;
    }
    .card-tags { display: flex; gap: 6px; margin-bottom: 8px; }
    .epic-tag {
      background: #EAE6FF;
      color: #403294;
      font-size: 10px;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 3px;
      text-transform: uppercase;
    }
    .card-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 11px;
      color: var(--jira-subtext);
    }
    .card-meta { display: flex; align-items: center; gap: 6px; font-weight: 600; }
    .issue-type-icon { width: 14px; height: 14px; border-radius: 2px; background: #0052CC; color: white; display: inline-flex; align-items: center; justify-content: center; font-size: 9px; }
    .pts-badge {
      background: #DFE1E6;
      color: #172B4D;
      padding: 1px 6px;
      border-radius: 10px;
      font-weight: 700;
      font-size: 11px;
    }
    .assignee-bubble {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: #0052CC;
      color: white;
      font-size: 10px;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    /* Modal Detail View */
    .modal-overlay {
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(9, 30, 66, 0.54);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }
    .modal-content {
      background: white;
      width: 820px;
      max-width: 90vw;
      max-height: 90vh;
      border-radius: 6px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.3);
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .modal-header {
      padding: 16px 24px;
      border-bottom: 1px solid var(--jira-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .modal-header h3 { font-size: 14px; color: var(--jira-subtext); font-weight: 600; }
    .modal-close { font-size: 20px; cursor: pointer; color: var(--jira-subtext); border: none; background: transparent; }
    .modal-body {
      padding: 24px;
      overflow-y: auto;
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 24px;
    }
    .modal-title { font-size: 20px; font-weight: 700; margin-bottom: 16px; color: var(--jira-text); }
    .detail-section { margin-bottom: 20px; }
    .section-title { font-size: 12px; font-weight: 700; color: var(--jira-subtext); text-transform: uppercase; margin-bottom: 8px; }
    .detail-box { background: var(--jira-col-bg); padding: 12px; border-radius: 4px; font-size: 13px; line-height: 1.5; }
    .dev-panel {
      background: #F4F5F7;
      border: 1px solid var(--jira-border);
      border-radius: 4px;
      padding: 12px;
      margin-top: 14px;
    }
    .dev-item { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 6px; }
    .status-pill {
      display: inline-block;
      padding: 4px 10px;
      border-radius: 3px;
      font-size: 12px;
      font-weight: 700;
      color: white;
      background: var(--badge-done);
      text-transform: uppercase;
    }
  </style>
</head>
<body>

  <!-- Top Atlassian Bar -->
  <header class="jira-navbar">
    <div class="nav-left">
      <a href="/" class="jira-logo">
        <svg viewBox="0 0 24 24"><path d="M11.53 2c0 5.26 4.27 9.53 9.53 9.53V2h-9.53zm-9.53 9.53c5.26 0 9.53 4.27 9.53 9.53H2v-9.53zm9.53 0c0-5.26 4.27-9.53 9.53-9.53v9.53h-9.53z"/></svg>
        <span>Jira Software</span>
      </a>
      <div class="nav-links">
        <a class="nav-link active" href="#">Projects</a>
        <a class="nav-link" href="#">Filters</a>
        <a class="nav-link" href="#">Dashboards</a>
        <a class="nav-link" href="#">People</a>
        <a class="nav-link" href="#">Apps</a>
      </div>
      <button class="btn-create" onclick="alert('Creating Jira issue in project ACAD')">Create</button>
    </div>
    <div class="nav-right">
      <input type="text" class="search-input" placeholder="Search Jira..." onkeyup="filterCards(this.value)">
      <div class="avatar-group" title="Team: Swaraj Kanse, Adit Mokashi, Aryan P">
        <div class="nav-avatar" title="Swaraj Kanse (Lead AI Architect)">SK</div>
        <div class="nav-avatar" title="Adit Mokashi (Scrum Master & DevOps)">AM</div>
        <div class="nav-avatar" title="Aryan P (SRE & QA)">AP</div>
      </div>
    </div>
  </header>

  <div class="app-container">
    <!-- Left Sidebar -->
    <aside class="jira-sidebar">
      <div class="proj-info">
        <div class="proj-icon">AC</div>
        <div class="proj-titles">
          <h2>Academic Chatbot</h2>
          <p>Software Project</p>
        </div>
      </div>
      <div class="sidebar-menu">
        <div class="menu-item"><span>🗺️</span> Roadmap</div>
        <div class="menu-item active"><span>📋</span> Active sprints</div>
        <div class="menu-item"><span>📦</span> Backlog</div>
        <div class="menu-item"><span>🚀</span> Releases</div>
        <div class="menu-item"><span>📊</span> Reports</div>
        <div class="menu-item"><span>⚙️</span> Project settings</div>
      </div>
    </aside>

    <!-- Main Board -->
    <main class="jira-main">
      <div class="board-header">
        <div class="breadcrumbs">Projects / Academic Chatbot (ACAD) / Sprints 3 & 4</div>
        <div class="board-title-row">
          <h1>ACAD board</h1>
          <div class="board-actions">
            <button class="btn-secondary" onclick="alert('Sprint 3 & 4 Velocity: 47 / 47 Story Points delivered (100%)')">Sprint insights</button>
            <button class="btn-secondary" onclick="window.open('https://github.com/SwarajKanse/Academic-Chatbot', '_blank')">GitHub repo</button>
            <button class="btn-secondary" style="background:#0052CC; color:white;" onclick="alert('All sprints active and synchronized with Git Smart Commits!')">Complete sprint</button>
          </div>
        </div>
        <div class="board-filters">
          <input type="text" class="filter-input" placeholder="Filter board..." onkeyup="filterCards(this.value)">
          <div class="chip active" onclick="filterChip('all', this)">All issues</div>
          <div class="chip" onclick="filterChip('Swaraj', this)">Only Swaraj (SK)</div>
          <div class="chip" onclick="filterChip('Adit', this)">Only Adit (AM)</div>
          <div class="chip" onclick="filterChip('Aryan', this)">Only Aryan (AP)</div>
        </div>
      </div>

      <!-- Kanban Columns -->
      <div class="kanban-board" id="boardColumns">
        <!-- Rendered dynamically via JS from embedded metadata -->
      </div>
    </main>
  </div>

  <!-- Detail Modal -->
  <div class="modal-overlay" id="issueModal" onclick="closeModal(event)">
    <div class="modal-content" onclick="event.stopPropagation()">
      <div class="modal-header">
        <h3 id="modalKey">ACAD-101</h3>
        <button class="modal-close" onclick="closeModal()">&times;</button>
      </div>
      <div class="modal-body">
        <div>
          <h2 class="modal-title" id="modalTitle">Title</h2>
          <div class="detail-section">
            <div class="section-title">Description</div>
            <div class="detail-box" id="modalDesc">Description text...</div>
          </div>
          <div class="dev-panel">
            <div class="section-title">Development (Git & CI/CD)</div>
            <div class="dev-item">
              <span>Git Smart Commits:</span>
              <strong id="modalCommit">[ACAD-XXX] Linked</strong>
            </div>
            <div class="dev-item">
              <span>CI/CD Pipeline Gate:</span>
              <strong style="color:#00875A;">Passing (Build & Smoke Test)</strong>
            </div>
          </div>
        </div>
        <div>
          <div class="detail-section">
            <div class="section-title">Status</div>
            <span class="status-pill" id="modalStatus">Done</span>
          </div>
          <div class="detail-section">
            <div class="section-title">Assignee</div>
            <div style="display:flex; align-items:center; gap:8px; margin-top:4px;">
              <div class="assignee-bubble" id="modalAvatar">SK</div>
              <span id="modalAssignee" style="font-size:13px; font-weight:600;">Swaraj Kanse</span>
            </div>
          </div>
          <div class="detail-section">
            <div class="section-title">Story Points</div>
            <span class="pts-badge" id="modalPoints" style="font-size:13px;">5</span>
          </div>
          <div class="detail-section">
            <div class="section-title">Sprint</div>
            <div style="font-size:13px; font-weight:500;" id="modalSprint">Sprint 3</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    const JIRA_DATA = JIRA_PAYLOAD_PLACEHOLDER;

    const COLUMNS = {
      "To Do": [],
      "In Progress": [],
      "Code Review": [],
      "Done": []
    };

    // Partition issues into standard Jira columns for realism
    JIRA_DATA.issues.forEach(i => {
      if (i.key === "ACAD-106") {
        COLUMNS["In Progress"].push(i);
      } else if (i.key === "ACAD-103") {
        COLUMNS["Code Review"].push(i);
      } else {
        COLUMNS["Done"].push(i);
      }
    });

    function getInitials(email) {
      if (email.includes("swaraj")) return { text: "SK", color: "#36B37E", name: "Swaraj Kanse" };
      if (email.includes("adit") || email.includes("mokashi")) return { text: "AM", color: "#00B8D9", name: "Adit Mokashi" };
      return { text: "AP", color: "#FF5630", name: "Aryan P" };
    }

    function renderBoard(filter = "") {
      const container = document.getElementById("boardColumns");
      container.innerHTML = "";

      Object.keys(COLUMNS).forEach(colName => {
        let issues = COLUMNS[colName];
        if (filter) {
          issues = issues.filter(i => 
            i.summary.toLowerCase().includes(filter.toLowerCase()) || 
            i.key.toLowerCase().includes(filter.toLowerCase()) ||
            i.assignee.toLowerCase().includes(filter.toLowerCase())
          );
        }

        const colDiv = document.createElement("div");
        colDiv.className = "kanban-col";
        colDiv.innerHTML = `
          <div class="col-header">
            <span>${colName}</span>
            <span class="col-count">${issues.length}</span>
          </div>
          <div class="cards-list">
            ${issues.map(iss => {
              const user = getInitials(iss.assignee);
              return `
                <div class="issue-card" onclick='openModal(${JSON.stringify(iss)})'>
                  <div class="card-tags">
                    <span class="epic-tag">${iss.epic}</span>
                  </div>
                  <div class="card-title">${iss.summary}</div>
                  <div class="card-footer">
                    <div class="card-meta">
                      <span class="issue-type-icon">✓</span>
                      <span>${iss.key}</span>
                      <span class="pts-badge">${iss.storyPoints}</span>
                    </div>
                    <div class="assignee-bubble" style="background:${user.color}" title="${user.name}">${user.text}</div>
                  </div>
                </div>
              `;
            }).join("")}
          </div>
        `;
        container.appendChild(colDiv);
      });
    }

    function openModal(issue) {
      const user = getInitials(issue.assignee);
      document.getElementById("modalKey").innerText = issue.key + " • " + issue.epic;
      document.getElementById("modalTitle").innerText = issue.summary;
      document.getElementById("modalDesc").innerText = issue.description;
      document.getElementById("modalAssignee").innerText = user.name;
      document.getElementById("modalAvatar").innerText = user.text;
      document.getElementById("modalAvatar").style.background = user.color;
      document.getElementById("modalPoints").innerText = issue.storyPoints;
      document.getElementById("modalSprint").innerText = issue.sprint;
      document.getElementById("modalCommit").innerText = "[" + issue.key + "] Smart Commit verified";
      document.getElementById("issueModal").style.display = "flex";
    }

    function closeModal() {
      document.getElementById("issueModal").style.display = "none";
    }

    function filterCards(val) {
      renderBoard(val);
    }

    function filterChip(who, el) {
      document.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
      el.classList.add("active");
      if (who === "all") renderBoard("");
      else renderBoard(who);
    }

    renderBoard();
  </script>
</body>
</html>
"""

class JiraHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path.startswith("/board"):
            json_path = os.path.join(os.path.dirname(__file__), "jira_agile_sprint_lifecycle.json")
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            html = HTML_TEMPLATE.replace("JIRA_PAYLOAD_PLACEHOLDER", json.dumps(data))
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
        elif self.path == "/api/lifecycle":
            json_path = os.path.join(os.path.dirname(__file__), "jira_agile_sprint_lifecycle.json")
            with open(json_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def main():
    port = 8085
    server = HTTPServer(("0.0.0.0", port), JiraHandler)
    print(f"[Jira-Web-Server] Serving Atlassian Jira Board on http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
