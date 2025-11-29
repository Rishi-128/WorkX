# WorkX - Anonymous Student Work Exchange Platform

WorkX is a campus-focused micro-service platform that enables students to request academic tasks such as blue book writing, observations, records, PPTs, Word documents, and reports. The platform ensures complete anonymity between users and writers by routing all submissions through an admin.

## 🚀 Features

### Core Features

- **Complete Anonymity**: Users never meet writers. All communication through admin.
- **Multiple Work Types**: Blue Books, Observations, Records, PPTs, Word Docs, Reports
- **Transparent Pricing**: Fixed 12% platform fee on all orders
- **Admin-Controlled Workflow**: Admin manages task assignment and file delivery
- **Offline Payments**: No online payment gateway, admin handles all transactions
- **Task Tracking**: Users can track their orders with Task ID
- **Quality Verification**: Admin verifies all completed work before delivery

### User Features

- Submit work requests with file uploads
- Instant price calculation
- Track order status with Task ID
- Download completed work
- View transparent pricing

### Admin Features

- Dashboard with task statistics
- Manage all orders (Pending/Assigned/In Progress/Completed)
- Assign tasks to writers
- Upload completed work files
- Track payments from users
- Track payouts to writers
- Filter orders by status

## 🛠️ Tech Stack

**Frontend:**

- HTML5
- CSS3 (Modern, responsive design)
- JavaScript (Vanilla)

**Backend:**

- Python 3.8+
- Flask 3.0.0
- JSON-based task storage

**File Storage:**

- Local file system for uploads

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser

## 🔧 Installation & Setup

### 1. Clone or Download the Project

```bash
cd c:\Users\Rishi\Desktop\assignment_agent
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Verify Directory Structure

Ensure the following structure exists:

```
assignment_agent/
├── app.py
├── requirements.txt
├── tasks.json (will be created automatically)
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── main.js
├── templates/
│   ├── index.html
│   ├── pricing.html
│   ├── create_order.html
│   ├── admin.html
│   └── user_task.html
└── uploads/
    ├── user_files/
    └── completed_work/
```

### 4. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## 🌐 Accessing the Platform

- **Homepage**: http://localhost:5000/
- **Pricing**: http://localhost:5000/pricing
- **Create Order**: http://localhost:5000/create-order
- **Track Order**: http://localhost:5000/user-task
- **Admin Dashboard**: http://localhost:5000/admin

## 📖 How It Works

### For Users

1. **Visit Homepage**: Browse pricing and features
2. **Create Order**:
   - Select work type
   - Enter number of pages/units
   - Upload reference files (optional)
   - Provide contact info and deadline
   - Calculate and review price
   - Submit order
3. **Receive Task ID**: Save this ID to track your order
4. **Track Order**: Enter Task ID to check status
5. **Download Work**: When status is "Completed", download your files
6. **Pay Offline**: Pay admin after verifying work quality

### For Admin

1. **Access Dashboard**: Navigate to `/admin`
2. **View All Orders**: See statistics and list of all tasks
3. **Assign Tasks**:
   - Select a pending task
   - Enter Writer ID
   - Update status to "Assigned"
4. **Upload Completed Work**:
   - When writer submits, admin uploads the file
   - Status automatically updates to "Completed"
5. **Track Payments**:
   - Mark "Payment Received" when user pays
   - Mark "Writer Paid" after paying the writer

## 💰 Pricing Structure

| Work Type        | Base Price | Platform Fee (12%) | Final Price | Writer Gets |
| ---------------- | ---------- | ------------------ | ----------- | ----------- |
| Blue Book        | ₹15/page   | ₹2/page            | ₹17/page    | ₹15/page    |
| Observation      | ₹17/page   | ₹2/page            | ₹19/page    | ₹17/page    |
| Record (Ruled)   | ₹20/page   | ₹2/page            | ₹22/page    | ₹20/page    |
| Record (Unruled) | ₹15/page   | ₹2/page            | ₹17/page    | ₹15/page    |
| PPT (10 slides)  | ₹50-₹70    | ₹6-₹8              | ₹56-₹78     | ₹50-₹70     |
| Word Document    | ₹50        | ₹6                 | ₹56         | ₹50         |
| Report           | ₹100       | ₹12                | ₹112        | ₹100        |

## 📁 File Upload Limits

- **Maximum file size**: 16MB per file
- **Allowed formats**: PDF, DOC, DOCX, TXT, PNG, JPG, JPEG
- **Multiple files**: Supported for user uploads

## 🔐 Security & Privacy

- **No user-writer contact**: Complete anonymity maintained
- **Offline payments only**: No sensitive financial data stored
- **Local file storage**: All files stored securely on server
- **Admin verification**: Quality control before delivery

## 🗃️ Data Storage

The application uses a JSON file (`tasks.json`) to store task data. Each task contains:

```json
{
  "task_id": "WXABC123",
  "work_type": "Blue Book",
  "pages": 10,
  "base_price": 150,
  "platform_fee": 20,
  "final_price": 170,
  "worker_payout": 150,
  "user_contact": "9876543210",
  "user_uploaded_files": ["file1.pdf"],
  "admin_uploaded_result": "WXABC123_completed.pdf",
  "status": "Completed",
  "deadline": "2025-11-20",
  "writer_id": "WR-001",
  "notes": "Special instructions",
  "created_at": "2025-11-15T10:30:00",
  "payment_received": true,
  "writer_paid": false
}
```

## 🎨 Design Features

- **Modern UI**: Clean, professional design with shadows and gradients
- **Responsive**: Works on desktop, tablet, and mobile
- **Color-coded Status**: Easy visual identification of task states
- **Interactive Cards**: Hover effects and smooth transitions
- **Timeline View**: Visual progress tracker for users

## 🔄 Workflow

```
User → Admin → Writer → Admin → User
```

1. **User submits order** → Admin receives
2. **Admin assigns to writer** → Writer works on task
3. **Writer completes** → Submits to admin
4. **Admin verifies quality** → Uploads for user
5. **User downloads** → Pays admin offline
6. **Admin collects payment** → Pays writer

## 🚨 Troubleshooting

### Port Already in Use

```bash
# Change port in app.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Upload Folder Permissions

Ensure the `uploads/` directory has write permissions:

```bash
# On Windows PowerShell
icacls uploads /grant Users:F /T
```

### Tasks Not Saving

Check that `tasks.json` is writable. If it doesn't exist, it will be created automatically.

## 📝 API Endpoints

### Public Endpoints

- `GET /` - Homepage
- `GET /pricing` - Pricing page
- `GET /create-order` - Create order page
- `GET /user-task` - Track order page
- `POST /api/calculate_price` - Calculate order price
- `POST /api/create_task` - Create new order
- `GET /api/user/task/<task_id>` - Get task details
- `GET /api/download/<task_id>` - Download completed file

### Admin Endpoints

- `GET /admin` - Admin dashboard
- `GET /api/admin/tasks` - Get all tasks
- `POST /api/admin/update_task` - Update task details
- `GET /api/rate_card` - Get pricing information

## 🎯 Future Enhancements

- User authentication system
- Writer portal for direct uploads
- Email notifications
- SMS alerts for status updates
- Payment tracking dashboard
- Analytics and reporting
- Multi-admin support
- Database integration (PostgreSQL/MySQL)

## 📄 License

This project is for educational purposes.

## 👥 Support

For issues or questions:

1. Check the troubleshooting section
2. Review the workflow documentation
3. Contact system administrator

## 🎓 Campus Use

WorkX is designed specifically for campus environments where:

- Students need academic work assistance
- Anonymity is crucial
- Offline payment is preferred
- Quality verification is mandatory
- Fair pricing for all parties is essential

---

**Built with ❤️ for Student Communities**

© 2025 WorkX - Campus Work Exchange Platform
