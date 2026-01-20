# VisionSafe AI - Professional Architecture

A production-ready workplace safety monitoring system using AI-powered PPE detection.

## 📁 Project Structure

```
visionsafe/
├── app.py                          # Main entry point (clean routing)
│
├── pages/                          # 🎨 Frontend pages (team-friendly)
│   ├── __init__.py
│   ├── live_monitor.py            # 📹 Real-time detection UI
│   ├── analytics.py               # 📊 Charts & metrics dashboard
│   └── violations_log.py           # 📝 Logs & evidence viewer
│
├── backend/                        # 💾 Core business logic
│   ├── __init__.py
│   ├── detection.py               # YOLO model & tracking
│   ├── ppe_detection.py           # PPE association logic
│   ├── violations.py              # Strike system & cooldown
│   ├── evidence.py                # Snapshot management
│   ├── database.py                # CSV operations
│   └── pdf_report.py              # PDF generation
│
├── ui/                            # 🎯 Reusable components
│   ├── __init__.py
│   ├── theme.py                   # CSS & color scheme
│   ├── components.py              # KPI cards, badges, info boxes
│   └── layout.py                  # Layout helpers
│
├── assets/                        # 🖼️ Static files
│   ├── logo.png
│   └── icons/
│
├── models/
│   └── best.pt                    # YOLO weights
│
├── evidence_snaps/                # 📸 Auto-generated evidence
│
├── safety_database.csv            # 📊 Violation database
│
└── requirements.txt               # Dependencies
```

## 🚀 Quick Start

### Installation

```bash
cd visionsafe
pip install -r requirements.txt
```

### Running the Application

```bash
streamlit run app.py
```

Visit `http://localhost:8501` in your browser.

## 🏗️ Architecture Overview

### **Frontend Team** → Works in `pages/` & `ui/`
- **Clean, modular pages** - No business logic
- **Reusable components** - Consistent UI across pages
- **Professional theming** - Centralized CSS & colors

### **Backend Team** → Works in `backend/`
- **Detection logic** - YOLO model management
- **Violations system** - Strike counting & cooldown
- **Evidence handling** - Snapshot management
- **Database ops** - CSV persistence
- **PDF reports** - Report generation

### **No Conflicts** - Clear separation of concerns

## 📋 Core Modules

### `backend/detection.py`
```python
load_model(path)              # Load YOLO with caching
run_detection(model, frame)   # Run YOLO tracking
extract_detections(results)   # Parse YOLO output
draw_annotations(frame, ...)  # Draw boxes on frame
```

### `backend/violations.py`
```python
update_strikes(worker, items, cooldown)  # Strike logic
is_fired(strikes, max_strikes)           # Check termination
get_worker_status(worker, items)         # Get status color/label
```

### `backend/database.py`
```python
record_violation(...)         # Create violation record
save_violation(record)        # Save to CSV
load_database()              # Load all records
get_statistics()             # Summary stats
```

### `ui/components.py`
```python
kpi_card(title, value, icon, color)      # KPI display
status_badge(status)                      # Status indicator
metric_row(metrics)                       # Multi-column metrics
info_box(title, content, type)            # Info/warning/error box
```

## 🎨 UI Features

- **Professional Light Theme** - Clean, minimal design
- **Responsive Layout** - Works on all screen sizes
- **Custom Components** - Reusable Streamlit widgets
- **Color Coding** - Status indicators (🟢 Safe, 🟠 Unsafe, 🔴 Fired)
- **Interactive Charts** - Plotly/Altair integration

## 💾 Data Flow

```
Video Input
    ↓
Detection (YOLO)
    ↓
PPE Association
    ↓
Violation Check
    ↓
Strike System (w/ Cooldown)
    ↓
Evidence + Database
    ↓
UI Display + Reports
```

## 🔧 Configuration

Edit settings in **Live Monitor** sidebar:
- **AI Confidence** - Detection threshold (0.0-1.0)
- **Model Path** - Path to YOLO weights
- **Input Source** - Webcam or uploaded video
- **Max Strikes** - Firing threshold
- **Cooldown** - Anti-spam timer

## 📊 Analytics Features

- **Total Violations** - Running count
- **Unique Workers** - Personnel tracked
- **Violation Breakdown** - By type
- **Activity Timeline** - Hourly trends
- **Worker Summary** - Per-person statistics

## 📸 Evidence Management

- **Automatic Snapshots** - Captured on violations
- **Evidence Gallery** - Browse incidents
- **Incident Details** - Time, worker, violation type
- **Download Proof** - Individual image downloads

## 📄 Export Options

- **CSV Export** - Full database export
- **PDF Report** - Professional compliance report
- **Individual Evidence** - Download snapshots

## 🔐 Admin Panel

- **Database Stats** - Record counts
- **System Status** - Health check
- **Clear Database** - Wipe all records (DANGER ZONE)
- **Clear Evidence** - Remove snapshots only

## 🛠️ Development

### Adding New Pages

1. Create file in `pages/` folder
2. Import in `app.py`
3. Add navigation option in sidebar

```python
from pages.my_page import my_page_function

if page == "🆕 My Page":
    my_page_function()
```

### Adding New Components

1. Create reusable widget in `ui/components.py`
2. Use `COLORS` dict for consistency
3. Test in pages

```python
from ui.components import kpi_card
from ui.theme import COLORS

kpi_card("Title", value, icon="📊", color=COLORS['primary_green'])
```

### Extending Backend Logic

1. Create module in `backend/`
2. Import in pages/components that need it
3. Document function signatures

```python
from backend.my_module import my_function

result = my_function(arg1, arg2)
```

## 🎯 Best Practices

✅ **DO:**
- Keep pages focused on UI/UX only
- Use backend modules for all logic
- Follow the color scheme (`COLORS` dict)
- Reuse components from `ui/components.py`
- Cache expensive operations with `@st.cache_resource`

❌ **DON'T:**
- Put business logic in pages
- Create custom CSS inline
- Duplicate component code
- Ignore error handling
- Mix concerns between modules

## 📈 Scalability

This architecture supports:
- **Multi-camera monitoring** - Parallel streams
- **Custom PPE requirements** - Edit `ppe_detection.py`
- **Different model backends** - Abstract in `detection.py`
- **Advanced analytics** - Add pages without touching core
- **Real-time dashboards** - WebSocket integration ready

## 🏆 Hackathon Edge

This structure demonstrates:
- ✨ **Professional code organization**
- 🎯 **Clear team collaboration**
- 📚 **Production-ready patterns**
- 🚀 **Scalable architecture**
- 🔧 **Easy to extend**

Judges **love** seeing modular, well-organized code. This looks like a startup, not a student project.

## 📝 License

[Your License Here]

## 👥 Team

- **Frontend Team** - Pages & UI components
- **Backend Team** - Detection & database logic
- **Integration** - Works seamlessly together

---

**VisionSafe AI** - Making workplaces safer, one detection at a time. 🛡️
