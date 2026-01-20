/**
 * VisionSafe API Connector
 * CONNECTS FRONTEND (Friend) TO BACKEND (You)
 */

// ✅ 1. YOUR PUBLIC API LINK (I put your link here for you)
const API_URL = "https://didactic-space-engine-7vj9rvw54979fx7jq-8000.app.github.dev";

// ==========================================
// 🔄 AUTO-UPDATE FUNCTION
// ==========================================
async function updateDashboard() {
    try {
        console.log("🔄 Fetching data from:", API_URL);

        // --- 1. GET STATS ---
        const resStats = await fetch(`${API_URL}/stats`);
        if (!resStats.ok) throw new Error("Stats unreachable");
        const stats = await resStats.json();

        // Update the Boxes (Matches your friend's HTML IDs)
        if (document.getElementById("total-violations")) 
            document.getElementById("total-violations").innerText = stats.total_violations || 0;

        if (document.getElementById("unique-violators")) 
            document.getElementById("unique-violators").innerText = stats.unique_workers || 0;

        if (document.getElementById("critical-issue")) 
            document.getElementById("critical-issue").innerText = stats.critical_issue || "-";


        // --- 2. GET LOGS ---
        const resLogs = await fetch(`${API_URL}/logs`);
        if (!resLogs.ok) throw new Error("Logs unreachable");
        const logs = await resLogs.json();

        // Update the Table
        const table = document.getElementById("logsTable");
        if (table) {
            table.innerHTML = ""; // Clear old rows
            
            if (logs.length === 0) {
                 table.innerHTML = `<tr><td colspan="4" class="text-center">No violations yet</td></tr>`;
            } else {
                logs.slice(0, 10).forEach(log => { // Show last 10
                    // Create the "View" button link
                    let btn = "-";
                    if (log.Evidence) {
                         // Extract filename from path
                         const filename = log.Evidence.split("/").pop();
                         btn = `<a href="${API_URL}/evidence/${filename}" target="_blank" class="btn btn-sm btn-primary">View</a>`;
                    }

                    table.innerHTML += `
                        <tr>
                            <td>${log.person_id || "-"}</td>
                            <td>${log.missing_ppe || "None"}</td>
                            <td>${log.timestamp || "-"}</td>
                            <td>${btn}</td>
                        </tr>
                    `;
                });
            }
        }

    } catch (err) {
        console.error("❌ Connection Failed:", err);
    }
}

// ==========================================
// 🚀 START THE ENGINE
// ==========================================

// 1. Run immediately when page loads
updateDashboard();

// 2. Refresh every 2 seconds
setInterval(updateDashboard, 2000);