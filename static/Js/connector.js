/**
 * VisionSafe API Connector
 * ✅ MATCHED TO SWAGGER UI: Uses /recent and /evidence/
 * ✅ INCLUDES VIDEO UPLOAD FEATURE
 */

// YOUR PUBLIC API LINK
// Ensure this matches the URL from your terminal where uvicorn is running
const API_URL = "https://didactic-space-engine-7vj9rvw54979fx7jq-8000.app.github.dev";

// ==========================================
// 1. DASHBOARD AUTO-UPDATE (Stats & Logs)
// ==========================================
async function updateDashboard() {
    try {
        // --- A. GET STATS (Top Row) ---
        const resStats = await fetch(`${API_URL}/stats`);
        
        if (resStats.ok) {
            const stats = await resStats.json();
            if (document.getElementById("total-violations")) 
                document.getElementById("total-violations").innerText = stats.total_violations || 0;
            if (document.getElementById("unique-violators")) 
                document.getElementById("unique-violators").innerText = stats.unique_workers || 0;
            if (document.getElementById("critical-issue")) 
                document.getElementById("critical-issue").innerText = stats.critical_issue || "-";
        }

        // --- B. GET LOGS (Table Data) ---
        const resLogs = await fetch(`${API_URL}/recent`); 

        if (resLogs.ok) {
            const logs = await resLogs.json();
            const table = document.getElementById("logsTable");
            
            if (table) {
                table.innerHTML = ""; // Clear old rows
                
                if (logs.length === 0) {
                     table.innerHTML = `<tr><td colspan="4" class="text-center">No violations yet</td></tr>`;
                } else {
                    logs.forEach(log => { 
                        // Intelligent Key Matching
                        const id = log.person_id || log.ID || "-";
                        const ppe = log.missing_ppe || log.Violation || "None";
                        const time = log.timestamp || log.Time || "-";
                        
                        // Handle Image Link
                        let btn = "-";
                        const imageFile = log.snapshot || log.Evidence || null;
                        
                        if (imageFile) {
                             const cleanName = imageFile.split("/").pop();
                             btn = `<a href="${API_URL}/evidence/${cleanName}" target="_blank" class="btn btn-sm btn-primary">View</a>`;
                        }

                        // Render Row
                        table.innerHTML += `
                            <tr>
                                <td>${id}</td>
                                <td>${ppe}</td>
                                <td>${time}</td>
                                <td>${btn}</td>
                            </tr>
                        `;
                    });
                }
            }
        }
    } catch (err) {
        console.error("❌ Connection Failed:", err);
    }
}

// ==========================================
// 2. VIDEO UPLOAD FEATURE (FIXED)
// ==========================================
async function processVideo() {
    const fileInput = document.getElementById("videoInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("⚠️ Please select a video file first.");
        return;
    }

    // Show Loading, Hide Upload
    document.getElementById("uploadSection").classList.add("d-none");
    document.getElementById("processingSection").classList.remove("d-none");

    const formData = new FormData();
    formData.append("file", file);

    try {
        console.log("📤 Uploading video...");
        const response = await fetch(`${API_URL}/upload_video`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        // ✅ FIXED LOGIC: Build the FULL URL using the API address
        if (data.status === "success" || data.filename) {
            
            // We use the filename to build the absolute link to the cloud server
            // This prevents the "localhost 404" error
            const cleanFilename = data.filename || data.video_url.split("/").pop();
            const fullVideoUrl = `${API_URL}/video/${cleanFilename}`;
            
            console.log("✅ Video ready at:", fullVideoUrl);
            
            const player = document.getElementById("videoPlayer");
            player.src = fullVideoUrl;
            player.load(); // Force reload to ensure new source plays
            player.play(); // Auto-play
            
            // Switch UI to Result View
            document.getElementById("processingSection").classList.add("d-none");
            document.getElementById("resultSection").classList.remove("d-none");
        } else {
            throw new Error(data.error || "Unknown error");
        }

    } catch (err) {
        console.error(err);
        alert("❌ Error: " + err.message);
        resetUpload(); // Reset UI on failure
    }
}

function resetUpload() {
    // Reset UI back to start
    document.getElementById("resultSection").classList.add("d-none");
    document.getElementById("processingSection").classList.add("d-none");
    document.getElementById("uploadSection").classList.remove("d-none");
    document.getElementById("videoInput").value = ""; 
}

// ==========================================
// 3. START ENGINE
// ==========================================
updateDashboard();
setInterval(updateDashboard, 2000); // Auto-refresh every 2s