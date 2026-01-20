# 🔗 VisionSafe API Connection Guide

**For Your Frontend Team**

---

## ✅ Quick Start

### 1. Get the API URL
1. Open VS Code (your partner's machine running the backend)
2. Look at the **PORTS** tab at the bottom
3. Find port **8000**
4. Right-click the **Forwarded Address** and copy it
   - Example: `https://didactic-space-engine-7vj9rvw54979fx7jq-8000.app.github.dev`

### 2. Update Your Code
Open `connector.js` and replace line 12:

```javascript
// BEFORE (localhost - only works on same machine)
const API_URL = "http://localhost:8000";

// AFTER (your public forwarded address)
const API_URL = "https://didactic-space-engine-7vj9rvw54979fx7jq-8000.app.github.dev";
```

**Important:** No trailing slash (`/`) at the end!

### 3. Include in Your HTML
```html
<script src="connector.js"></script>
<script>
    // Initialize on page load
    window.addEventListener('load', initDashboard);
</script>
```

### 4. Use the Functions
```html
<!-- Add elements with these IDs to your HTML -->
<h1 id="violation-count">Loading...</h1>
<h2 id="worker-count">Loading...</h2>
<p id="critical-issue">Loading...</p>

<!-- Update them with JavaScript -->
<script>
    async function updateDashboard() {
        const stats = await getStats();
        if (stats) {
            document.getElementById("violation-count").innerText = stats.total_violations;
            document.getElementById("worker-count").innerText = stats.unique_workers;
            document.getElementById("critical-issue").innerText = stats.critical_issue;
        }
    }
    
    // Update every 2 seconds
    setInterval(updateDashboard, 2000);
    updateDashboard(); // Run immediately
</script>
```

---

## 📚 Available API Functions

### `getStats()`
Returns live dashboard statistics:
```javascript
const stats = await getStats();
// {
//   total_violations: 52,
//   unique_workers: 8,
//   critical_issue: "Missing Helmet",
//   status: "live"
// }
```

### `getRecentViolations(limit)`
Get recent incidents (default last 10):
```javascript
const violations = await getRecentViolations(5);
// [
//   {
//     Time: "2024-01-16 14:32:10",
//     ID: "Worker-1",
//     Violation: "Missing Helmet, Gloves",
//     Strikes: 3,
//     Evidence: "evidence_snaps/Worker1_14-32-10.jpg"
//   },
//   ...
// ]
```

### `getViolationsByType()`
For bar charts (violation breakdown):
```javascript
const breakdown = await getViolationsByType();
// {
//   "Missing Helmet": 15,
//   "Missing Gloves": 12,
//   "Missing Vest": 8,
//   ...
// }
```

### `getViolationsByHour()`
For timeline charts (hourly distribution):
```javascript
const hourly = await getViolationsByHour();
// {
//   "9": 2,
//   "10": 5,
//   "11": 8,
//   "12": 3,
//   ...
// }
```

### `getEvidenceURL(filename)`
Get URL for evidence images:
```javascript
const imageURL = getEvidenceURL("Worker1_14-32-10.jpg");
// <img src={imageURL} />
```

### `checkHealth()`
Verify API connection:
```javascript
const isConnected = await checkHealth();
if (isConnected) {
    console.log("✅ API is reachable!");
} else {
    console.log("❌ Cannot reach API");
}
```

---

## 🎨 HTML Example Template

```html
<!DOCTYPE html>
<html>
<head>
    <title>VisionSafe Dashboard</title>
    <style>
        body { font-family: Arial; background: #f5f5f5; }
        .card { background: white; padding: 20px; margin: 10px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .metric { font-size: 24px; font-weight: bold; color: #00C853; }
    </style>
</head>
<body>
    <h1>🛡️ VisionSafe Dashboard</h1>
    
    <div class="card">
        <h3>Total Violations</h3>
        <p class="metric" id="violation-count">Loading...</p>
    </div>
    
    <div class="card">
        <h3>Active Workers</h3>
        <p class="metric" id="worker-count">Loading...</p>
    </div>
    
    <div class="card">
        <h3>Critical Issue</h3>
        <p id="critical-issue">Loading...</p>
    </div>
    
    <script src="connector.js"></script>
    <script>
        async function updateDashboard() {
            const stats = await getStats();
            if (stats) {
                document.getElementById("violation-count").innerText = stats.total_violations;
                document.getElementById("worker-count").innerText = stats.unique_workers;
                document.getElementById("critical-issue").innerText = stats.critical_issue;
            }
        }
        
        // Load on page ready
        window.addEventListener('load', async () => {
            await updateDashboard();
            // Update every 2 seconds
            setInterval(updateDashboard, 2000);
        });
    </script>
</body>
</html>
```

---

## 🔧 Troubleshooting

### "Cannot fetch from API"
- Check your `API_URL` is correct and starts with `https://` (not `http://`)
- Make sure port 8000 is **Public** in the PORTS tab
- Check browser console (F12) for error messages

### "CORS Error"
- This is fixed by your backend—no action needed

### "API returns 404"
- Make sure you're using `/stats`, `/recent`, etc. (not just the root URL)

### Numbers aren't updating
- Open browser console (F12)
- Check for errors
- Verify API_URL has no trailing slash

---

## ✅ Checklist Before Demo

- [ ] Copied public forwarded address from PORTS tab
- [ ] Updated `API_URL` in `connector.js`
- [ ] No trailing slash in API_URL
- [ ] Included `connector.js` in your HTML
- [ ] Added element IDs (`violation-count`, `worker-count`, etc.)
- [ ] Tested in browser—numbers are live ✅

---

**Ready to demo!** 🚀
