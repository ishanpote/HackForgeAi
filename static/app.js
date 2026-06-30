document.addEventListener("DOMContentLoaded", () => {
    
    // API State and Selectors
    let activeProjectId = null;
    let pollingInterval = null;
    let currentProjectData = null;
    
    const views = {
        dashboard: document.getElementById("view-dashboard"),
        forge: document.getElementById("view-forge"),
        live: document.getElementById("view-live"),
        results: document.getElementById("view-results")
    };
    
    const navItems = {
        dashboard: document.getElementById("nav-dashboard"),
        forge: document.getElementById("nav-forge"),
        live: document.getElementById("nav-live"),
        results: document.getElementById("nav-results")
    };

    // Nav Switcher Logic
    function showView(viewName) {
        Object.keys(views).forEach(key => {
            if (key === viewName) {
                views[key].classList.add("active");
                navItems[key].classList.add("active");
            } else {
                views[key].classList.remove("active");
                navItems[key].classList.remove("active");
            }
        });
        
        // Hide/show live execution or results nav tabs if no active project
        if (viewName === "dashboard" || viewName === "forge") {
            if (!activeProjectId) {
                navItems.live.style.display = "none";
                navItems.results.style.display = "none";
            }
        }
    }

    // Set up click handlers for sidebar nav
    Object.keys(navItems).forEach(key => {
        navItems[key].addEventListener("click", (e) => {
            e.preventDefault();
            showView(key);
        });
    });

    document.getElementById("btn-dashboard-new").addEventListener("click", () => showView("forge"));
    document.getElementById("btn-create-first").addEventListener("click", () => showView("forge"));
    document.getElementById("btn-results-dashboard").addEventListener("click", () => showView("dashboard"));

    // Settings Modal Configuration
    const modal = document.getElementById("settings-modal");
    const apiKeyInput = document.getElementById("input-api-key");
    
    // Load saved API Key on startup
    const savedKey = localStorage.getItem("gemini_api_key");
    if (savedKey) {
        apiKeyInput.value = savedKey;
    }

    document.getElementById("btn-settings").addEventListener("click", () => {
        modal.style.display = "flex";
    });
    
    document.getElementById("btn-close-modal").addEventListener("click", () => {
        modal.style.display = "none";
    });
    
    document.getElementById("btn-save-api-key").addEventListener("click", () => {
        const key = apiKeyInput.value.trim();
        if (key) {
            localStorage.setItem("gemini_api_key", key);
        } else {
            localStorage.removeItem("gemini_api_key");
        }
        modal.style.display = "none";
        alert("Gemini settings saved successfully!");
    });
    
    document.getElementById("btn-clear-api-key").addEventListener("click", () => {
        localStorage.removeItem("gemini_api_key");
        apiKeyInput.value = "";
        modal.style.display = "none";
        alert("API Key cleared.");
    });

    // Dashboard Data Loading
    async function loadDashboard() {
        try {
            const res = await fetch("/api/projects");
            if (!res.ok) throw new Error("Failed to load projects list.");
            const projects = await res.json();
            
            // Render Stats
            document.getElementById("stat-total").textContent = projects.length;
            
            const completedCount = projects.filter(p => p.status === "COMPLETED").length;
            const rate = projects.length > 0 ? Math.round((completedCount / projects.length) * 100) : 0;
            document.getElementById("stat-success-rate").textContent = `${rate}%`;
            
            // Render Projects Table
            const tbody = document.getElementById("projects-tbody");
            tbody.innerHTML = "";
            
            if (projects.length === 0) {
                document.getElementById("dashboard-empty-state").style.display = "flex";
                document.getElementById("projects-table-wrapper").style.display = "none";
            } else {
                document.getElementById("dashboard-empty-state").style.display = "none";
                document.getElementById("projects-table-wrapper").style.display = "block";
                
                projects.forEach(project => {
                    const row = document.createElement("tr");
                    const date = new Date(project.created_at).toLocaleDateString(undefined, {
                        month: 'short', day: 'numeric', hour: '2-digit', minute:'2-digit'
                    });
                    
                    let statusClass = "pending";
                    if (project.status === "COMPLETED") statusClass = "completed";
                    else if (project.status === "RUNNING") statusClass = "running";
                    else if (project.status === "FAILED") statusClass = "failed";
                    
                    row.innerHTML = `
                        <td class="project-name-cell">${project.name}</td>
                        <td>${project.theme || "General"}</td>
                        <td><span class="status-badge ${statusClass}">${project.status}</span></td>
                        <td>${date}</td>
                        <td class="actions-col">
                            <div class="actions-cell">
                                <button class="icon-btn view-btn" data-id="${project.id}" title="View Blueprint">
                                    <i class="fa-solid fa-eye"></i>
                                </button>
                                <button class="icon-btn delete delete-btn" data-id="${project.id}" title="Delete">
                                    <i class="fa-solid fa-trash-can"></i>
                                </button>
                            </div>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
                
                // Add button listeners
                document.querySelectorAll(".view-btn").forEach(btn => {
                    btn.addEventListener("click", () => {
                        const pid = btn.getAttribute("data-id");
                        viewProjectBlueprint(pid);
                    });
                });
                
                document.querySelectorAll(".delete-btn").forEach(btn => {
                    btn.addEventListener("click", async () => {
                        const pid = btn.getAttribute("data-id");
                        if (confirm("Are you sure you want to delete this blueprint?")) {
                            await deleteProject(pid);
                        }
                    });
                });
            }
        } catch (err) {
            console.error(err);
        }
    }

    async function deleteProject(id) {
        try {
            const res = await fetch(`/api/projects/${id}`, { method: "DELETE" });
            if (!res.ok) throw new Error("Delete request failed.");
            loadDashboard();
        } catch (err) {
            alert("Failed to delete project: " + err.message);
        }
    }

    // Submission Forging Logic
    const forgeForm = document.getElementById("forge-form");
    forgeForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const payload = {
            name: document.getElementById("input-hack-name").value.trim(),
            theme: document.getElementById("input-theme").value.trim(),
            problem_statement: document.getElementById("input-problem").value.trim(),
            constraints: document.getElementById("input-constraints").value.trim(),
            tech_preferences: document.getElementById("input-tech").value.trim(),
        };
        
        const apiKey = localStorage.getItem("gemini_api_key");
        const headers = {
            "Content-Type": "application/json"
        };
        if (apiKey) {
            headers["x-gemini-key"] = apiKey;
        } else {
            // Warn the user but proceed to check if env key is available
            const proceed = confirm("No Gemini API key configured in local settings. We will check the server environment. Would you like to proceed?");
            if (!proceed) return;
        }
        
        try {
            document.getElementById("btn-forge-submit").disabled = true;
            document.getElementById("btn-forge-submit").innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Initializing AI Agency...';
            
            const res = await fetch("/api/projects", {
                method: "POST",
                headers: headers,
                body: JSON.stringify(payload)
            });
            
            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.detail || "Request failed.");
            }
            
            const data = await res.json();
            activeProjectId = data.project_id;
            
            // Set UI view to live execution
            navItems.live.style.display = "flex";
            showView("live");
            
            // Reset Form
            forgeForm.reset();
            
            // Reset Graph Nodes
            resetGraphNodes();
            
            // Clear Console Log
            document.getElementById("live-logs-terminal").innerHTML = `
                <div class="log-line system">[System] Connection established. Initializing multi-agent network...</div>
            `;
            
            // Start Polling
            startPolling(activeProjectId);
            
        } catch (err) {
            alert("Forging trigger failed: " + err.message);
        } finally {
            document.getElementById("btn-forge-submit").disabled = false;
            document.getElementById("btn-forge-submit").innerHTML = '<i class="fa-solid fa-screwdriver-wrench"></i> Forge Project Blueprint';
        }
    });

    // Workflow Graph Management
    function resetGraphNodes() {
        const nodes = [
            "planner", "idea", "research", "datasets", "tech", 
            "pitch", "architecture", "dev_planner", "readme", "reviewer", "pm"
        ];
        nodes.forEach(n => {
            const el = document.getElementById(`node-${n}`);
            if (el) {
                el.className = "agent-node pending";
            }
        });
        
        const lines = document.querySelectorAll(".flow-line");
        lines.forEach(l => {
            l.setAttribute("class", "flow-line");
        });
    }

    function updateGraphState(logs, projectStatus) {
        // Simple map of log patterns to node highlights
        const logText = logs.map(l => l.message).join("\n");
        
        const states = {
            planner: "pending",
            idea: "pending",
            research: "pending",
            datasets: "pending",
            tech: "pending",
            pitch: "pending",
            architecture: "pending",
            dev_planner: "pending",
            readme: "pending",
            reviewer: "pending",
            pm: "pending"
        };
        
        // Logical assertions based on progress messages
        // Planner Agent
        if (logText.includes("Planner Agent starting")) {
            states.planner = "running";
            document.getElementById("line-planner-idea").setAttribute("class", "flow-line active");
            document.getElementById("line-planner-research").setAttribute("class", "flow-line active");
        }
        if (logText.includes("Workflow plan finalized") || logText.includes("Idea Gen and Research Agents")) {
            states.planner = "completed";
            document.getElementById("line-planner-idea").setAttribute("class", "flow-line completed");
            document.getElementById("line-planner-research").setAttribute("class", "flow-line completed");
        }
        
        // Idea Gen & Research
        if (logText.includes("Brainstorming and scoring project ideas")) {
            states.idea = "running";
        }
        if (logText.includes("Idea generation complete")) {
            states.idea = "completed";
            document.getElementById("line-idea-datasets").setAttribute("class", "flow-line active");
            document.getElementById("line-idea-tech").setAttribute("class", "flow-line active");
            document.getElementById("line-idea-pitch").setAttribute("class", "flow-line active");
        }
        
        if (logText.includes("Searching the web for competitors")) {
            states.research = "running";
        }
        if (logText.includes("Competitor research completed")) {
            states.research = "completed";
            document.getElementById("line-research-pitch").setAttribute("class", "flow-line completed");
        }
        
        // Dataset Discovery, Tech, Pitch
        if (logText.includes("Searching for relevant datasets")) {
            states.datasets = "running";
        }
        if (logText.includes("Dataset discovery completed")) {
            states.datasets = "completed";
            document.getElementById("line-datasets-review").setAttribute("class", "flow-line completed");
        }
        
        if (logText.includes("Formulating custom tech stack")) {
            states.tech = "running";
        }
        if (logText.includes("Technology stack recommendations generated")) {
            states.tech = "completed";
            document.getElementById("line-tech-arch").setAttribute("class", "flow-line active");
            document.getElementById("line-tech-dev").setAttribute("class", "flow-line active");
            document.getElementById("line-idea-tech").setAttribute("class", "flow-line completed");
            document.getElementById("line-idea-datasets").setAttribute("class", "flow-line completed");
        }
        
        if (logText.includes("Formulating elevator pitch, presentation slide outline")) {
            states.pitch = "running";
        }
        if (logText.includes("Pitch presentation outlines generated")) {
            states.pitch = "completed";
            document.getElementById("line-pitch-review").setAttribute("class", "flow-line completed");
            document.getElementById("line-idea-pitch").setAttribute("class", "flow-line completed");
        }
        
        // System Architecture & Dev Planner
        if (logText.includes("Designing architecture and rendering")) {
            states.architecture = "running";
        }
        if (logText.includes("System architecture designed")) {
            states.architecture = "completed";
            document.getElementById("line-tech-arch").setAttribute("class", "flow-line completed");
            document.getElementById("line-arch-readme").setAttribute("class", "flow-line active");
            document.getElementById("line-arch-review").setAttribute("class", "flow-line active");
        }
        
        if (logText.includes("Creating milestones and development roadmap")) {
            states.dev_planner = "running";
        }
        if (logText.includes("Development roadmap formulated")) {
            states.dev_planner = "completed";
            document.getElementById("line-tech-dev").setAttribute("class", "flow-line completed");
            document.getElementById("line-dev-readme").setAttribute("class", "flow-line active");
            document.getElementById("line-dev-review").setAttribute("class", "flow-line active");
        }
        
        // README & Reviewer
        if (logText.includes("Drafting production-ready README")) {
            states.readme = "running";
        }
        if (logText.includes("README document generated")) {
            states.readme = "completed";
            document.getElementById("line-arch-readme").setAttribute("class", "flow-line completed");
            document.getElementById("line-dev-readme").setAttribute("class", "flow-line completed");
            document.getElementById("line-readme-pm").setAttribute("class", "flow-line active");
        }
        
        if (logText.includes("Auditing all generated artifacts")) {
            states.reviewer = "running";
        }
        if (logText.includes("Consistency review and checklist compiled")) {
            states.reviewer = "completed";
            document.getElementById("line-arch-review").setAttribute("class", "flow-line completed");
            document.getElementById("line-dev-review").setAttribute("class", "flow-line completed");
            document.getElementById("line-review-pm").setAttribute("class", "flow-line active");
        }
        
        // PM
        if (logText.includes("Compiling final project blueprint")) {
            states.pm = "running";
        }
        if (logText.includes("Project blueprint and executive summary compiled by PM") || projectStatus === "COMPLETED") {
            states.pm = "completed";
            document.getElementById("line-readme-pm").setAttribute("class", "flow-line completed");
            document.getElementById("line-review-pm").setAttribute("class", "flow-line completed");
        }
        
        // Mark failed nodes if failed
        if (projectStatus === "FAILED") {
            // Find running node and mark failed
            Object.keys(states).forEach(key => {
                if (states[key] === "running") states[key] = "failed";
            });
        }
        
        // Apply classes to UI
        Object.keys(states).forEach(key => {
            const el = document.getElementById(`node-${key}`);
            if (el) {
                el.className = `agent-node ${states[key]}`;
            }
        });
    }

    // Real-Time Log Poller
    function startPolling(projectId) {
        if (pollingInterval) clearInterval(pollingInterval);
        
        pollingInterval = setInterval(async () => {
            try {
                const res = await fetch(`/api/projects/${projectId}`);
                if (!res.ok) throw new Error("Could not fetch project status.");
                const data = await res.json();
                
                // Append logs
                const terminal = document.getElementById("live-logs-terminal");
                const logs = JSON.parse(data.logs);
                
                terminal.innerHTML = "";
                logs.forEach(log => {
                    const time = new Date(log.timestamp).toLocaleTimeString();
                    const logClass = log.agent.toLowerCase().replace(/\s+/g, "-");
                    
                    const line = document.createElement("div");
                    line.className = `log-line ${logClass}`;
                    line.innerHTML = `
                        <span class="timestamp">[${time}]</span>
                        <span class="agent">&lt;${log.agent}&gt;</span>
                        <span class="message">${log.message}</span>
                    `;
                    terminal.appendChild(line);
                });
                
                // Scroll to bottom
                terminal.scrollTop = terminal.scrollHeight;
                
                // Update graph
                updateGraphState(logs, data.status);
                
                // Check if completed/failed
                if (data.status === "COMPLETED") {
                    clearInterval(pollingInterval);
                    activeProjectId = null;
                    loadDashboard();
                    alert("Forging complete! Opening your brand new blueprint...");
                    viewProjectBlueprint(projectId);
                } else if (data.status === "FAILED") {
                    clearInterval(pollingInterval);
                    activeProjectId = null;
                    loadDashboard();
                    alert("Forging failed. Please check the terminal execution logs.");
                }
                
            } catch (err) {
                console.error("Polling error: ", err);
            }
        }, 1200);
    }

    // Results Blueprint Rendering
    async function viewProjectBlueprint(projectId) {
        try {
            const res = await fetch(`/api/projects/${projectId}`);
            if (!res.ok) throw new Error("Failed to load blueprint details.");
            const project = await res.json();
            currentProjectData = project;
            
            // Show Blueprint navigation link
            navItems.results.style.display = "flex";
            showView("results");
            
            // Set header title
            document.getElementById("results-project-name").textContent = project.name;
            document.getElementById("results-project-meta").textContent = `Theme: ${project.theme || "General"} / Created: ${new Date(project.created_at).toLocaleDateString()}`;
            
            // Set tabs listeners
            const resNavButtons = document.querySelectorAll(".res-nav-item");
            resNavButtons.forEach(btn => {
                btn.classList.remove("active");
                
                // Remove previous listeners
                const newBtn = btn.cloneNode(true);
                btn.parentNode.replaceChild(newBtn, btn);
                
                newBtn.addEventListener("click", () => {
                    document.querySelectorAll(".res-nav-item").forEach(b => b.classList.remove("active"));
                    newBtn.classList.add("active");
                    const secName = newBtn.getAttribute("data-section");
                    renderSection(secName);
                });
            });
            
            // Highlight and load first tab
            const firstTab = document.querySelector(".res-nav-item");
            firstTab.classList.add("active");
            renderSection(firstTab.getAttribute("data-section"));
            
        } catch (err) {
            alert("Error loading blueprint: " + err.message);
        }
    }

    // Markdown & Mermaid Integration
    async function renderSection(sectionName) {
        if (!currentProjectData) return;
        
        document.getElementById("current-section-title").textContent = sectionName;
        
        let markdown = "";
        if (sectionName === "Executive Summary") {
            markdown = currentProjectData.summary || "No executive summary available.";
        } else {
            const artifacts = JSON.parse(currentProjectData.artifacts);
            markdown = artifacts[sectionName] || "This section is empty.";
        }
        
        // Parse markdown content
        const renderedHtml = marked.parse(markdown);
        const container = document.getElementById("section-rendered-content");
        container.innerHTML = renderedHtml;
        
        // Compile and render Mermaid code blocks if they exist
        await renderMermaidDiagrams();
    }

    async function renderMermaidDiagrams() {
        const codeBlocks = document.querySelectorAll("#section-rendered-content pre code.language-mermaid");
        
        for (let block of codeBlocks) {
            const pre = block.parentElement;
            const code = block.textContent.trim();
            const id = "mermaid-" + Math.random().toString(36).substring(2, 11);
            
            try {
                // Render Mermaid code to SVG asynchronously
                const { svg } = await mermaid.render(id, code);
                const wrapper = document.createElement("div");
                wrapper.className = "mermaid-svg-wrapper";
                wrapper.style.display = "flex";
                wrapper.style.justifyContent = "center";
                wrapper.style.padding = "20px";
                wrapper.style.backgroundColor = "rgba(0,0,0,0.15)";
                wrapper.style.borderRadius = "8px";
                wrapper.style.margin = "16px 0";
                wrapper.innerHTML = svg;
                
                pre.replaceWith(wrapper);
            } catch (err) {
                console.error("Mermaid compile error: ", err);
                
                // Clear error state in Mermaid global to prevent lockouts
                const errElement = document.getElementById(id);
                if (errElement) errElement.remove();
                
                // Keep raw code format on failure so users can still read the diagram code
                pre.style.border = "1px solid rgba(236,72,153,0.3)";
            }
        }
    }

    // Copy to Clipboard helpers
    document.getElementById("btn-copy-section").addEventListener("click", () => {
        const title = document.getElementById("current-section-title").textContent;
        let content = "";
        
        if (title === "Executive Summary") {
            content = currentProjectData.summary;
        } else {
            const artifacts = JSON.parse(currentProjectData.artifacts);
            content = artifacts[title];
        }
        
        if (content) {
            copyToClipboard(content);
            alert(`Section "${title}" copied to clipboard!`);
        }
    });

    document.getElementById("btn-results-copy-all").addEventListener("click", () => {
        if (!currentProjectData) return;
        
        let fullDoc = `# Project Blueprint: ${currentProjectData.name}\n`;
        fullDoc += `Theme: ${currentProjectData.theme || "General"}\n`;
        fullDoc += `Problem Statement: ${currentProjectData.problem_statement}\n\n`;
        fullDoc += `## Executive Summary\n${currentProjectData.summary}\n\n`;
        
        const artifacts = JSON.parse(currentProjectData.artifacts);
        Object.keys(artifacts).forEach(key => {
            fullDoc += `## ${key}\n${artifacts[key]}\n\n`;
        });
        
        copyToClipboard(fullDoc);
        alert("Complete project blueprint copied to clipboard!");
    });

    function copyToClipboard(text) {
        const el = document.createElement("textarea");
        el.value = text;
        document.body.appendChild(el);
        el.select();
        document.execCommand("copy");
        document.body.removeChild(el);
    }

    document.getElementById("btn-clear-logs").addEventListener("click", () => {
        document.getElementById("live-logs-terminal").innerHTML = `
            <div class="log-line system">[System] Logs cleared by user.</div>
        `;
    });

    // App Initialization
    loadDashboard();
    
    // Interval to refresh dashboard stats in background
    setInterval(loadDashboard, 15000);
});
