# WorkX - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

Open PowerShell in the project directory and run:

```powershell
pip install -r requirements.txt
```

### Step 2: Start the Server

```powershell
python app.py
```

You should see:

```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

### Step 3: Open Your Browser

Navigate to: **http://localhost:5000**

## 🎯 Quick Test

### Test as User:

1. Go to http://localhost:5000/create-order
2. Select "Blue Book"
3. Enter 5 pages
4. Fill in contact: 9876543210
5. Set deadline (tomorrow)
6. Click "Calculate Price"
7. Click "Submit Order"
8. **SAVE THE TASK ID!** (e.g., WXABC123)

### Test as Admin:

1. Go to http://localhost:5000/admin
2. You'll see your order in "Pending" status
3. Click "Manage" button
4. Enter Writer ID: WR-001
5. Change status to "Assigned"
6. Upload a test file (any PDF/Word doc)
7. Check "Payment Received"
8. Click "Update Task"

### Test Order Tracking:

1. Go to http://localhost:5000/user-task
2. Enter your Task ID (from Step 1)
3. Click "Track Order"
4. See the status and download button

## 🎉 That's It!

Your WorkX platform is now fully operational!

## 📱 All Pages

- **Homepage**: http://localhost:5000/
- **Pricing**: http://localhost:5000/pricing
- **Create Order**: http://localhost:5000/create-order
- **Track Order**: http://localhost:5000/user-task
- **Admin Dashboard**: http://localhost:5000/admin

## 💡 Tips

- Task IDs are automatically generated (format: WX + 6 random chars)
- Files are stored in `uploads/` folder
- All task data is saved in `tasks.json`
- No database required!
- Admin page has no authentication (add it if needed for production)

## ⚠️ Important Notes

- This is a development server (Flask debug mode)
- For production, use a proper WSGI server (Gunicorn, uWSGI)
- Add authentication for admin panel in production
- Consider using a real database (PostgreSQL/MySQL) for production

## 🐛 Common Issues

**Port 5000 already in use?**
Change port in app.py:

```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Can't upload files?**
Check folder permissions:

```powershell
icacls uploads /grant Users:F /T
```

**Tasks not saving?**
Make sure the application has write permissions in the current directory.

---

**Happy Building! 🚀**
