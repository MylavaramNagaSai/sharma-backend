from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Field, Session, SQLModel, create_engine, select
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication # <-- Added for PDF attachments
# --- 1. THE MODELS ---
class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    duration: str
    cost: str
    contents: str
    seats: int

class Certificate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cert_code: str = Field(unique=True, index=True)
    student_name: str
    course: str
    marks: str
    validity: str

class Program(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    icon: str
    features: str

class Testimonial(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    role: str
    content: str
    rating: int
    image_url: str

class Announcement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    message: str

class AdminConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password: str
    reset_code: Optional[str] = None

# --- 2. THE ENGINE ---
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

app = FastAPI(title="Sharma Soft Skills Pro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    with Session(engine) as session:
        if not session.exec(select(Course)).first():
            session.add_all([
                Course(name="Introduction to Soft Skills", duration="3 Hours", cost="₹4,999", contents="Concept of soft skills, importance, self-awareness, and personal development.", seats=30),
                Course(name="Communication Skills", duration="6 Hours", cost="₹5,499", contents="Verbal and non-verbal communication, listening skills, presentations, digital etiquette.", seats=25),
                Course(name="Teamwork & Interpersonal Skills", duration="5 Hours", cost="₹4,999", contents="Team dynamics, leadership basics, conflict management, and collaboration.", seats=15),
                Course(name="Time Management & Goal Setting", duration="4 Hours", cost="₹3,999", contents="SMART goals, prioritization, planning techniques, and productivity improvement.", seats=8),
                Course(name="Emotional Intelligence & Stress Management", duration="5 Hours", cost="₹5,999", contents="Self-regulation, empathy, handling stress, and emotional control strategies.", seats=12),
                Course(name="Critical Thinking & Problem Solving", duration="4 Hours", cost="₹4,499", contents="Logical reasoning, creativity, decision making, and real-world case analysis.", seats=20),
                Course(name="Professional Skills & Career Readiness", duration="3 Hours", cost="₹3,499", contents="Professional ethics, interview skills, resume basics, and workplace behaviour.", seats=5)
            ])
        if not session.exec(select(Program)).first():
            session.add_all([
                Program(title="Spoken English & Communication Skills", icon="FaMicrophone", features="Beginner to Advanced Spoken English\nWorkplace Communication (Emails, Meetings)\nAccent Neutralization\nClient Communication Skills"),
                Program(title="Public Speaking & Presentation Skills", icon="FaChalkboardTeacher", features="Overcome Stage Fear\nCorporate Presentation Skills\nTeam Meeting Confidence\nVoice & Body Language Mastery"),
                Program(title="Personality Development", icon="FaUserTie", features="Confidence Building for Professionals\nCorporate Grooming & Etiquette\nPositive Mindset Training\nEmotional Intelligence"),
                Program(title="Interview Preparation", icon="FaFileAlt", features="HR & Technical Mock Interviews\nResume Building for IT & Non-IT Roles\nGroup Discussion Practice\nStartup & MNC Interview Training"),
                Program(title="Corporate & Leadership Skills", icon="FaChartLine", features="Leadership Communication\nTeam Collaboration Skills\nTime & Stress Management\nProblem Solving for Workplace")
            ])
        if not session.exec(select(Testimonial)).first():
            session.add_all([
                Testimonial(name="Sri Lakshmi", role="EEE Student", content="Sharma Sir's training helped me build stronger communication skills, boost my confidence, and create a more professional presence.", rating=5, image_url="https://ui-avatars.com/api/?name=Sri+Lakshmi&background=2a364b&color=fff"),
                Testimonial(name="Rajesh", role="TCS Employee", content="The workshops on presentation skills and communication strategies were excellent and helped raise the bar of our team's communication.", rating=5, image_url="https://ui-avatars.com/api/?name=Rajesh&background=d97706&color=fff"),
                Testimonial(name="Arjun", role="Corporate Training Program", content="The team-building workshop was engaging, fun, and highly relevant to improving team dynamics in our organisation.", rating=5, image_url="https://ui-avatars.com/api/?name=Arjun&background=2a364b&color=fff"),
                Testimonial(name="Sai", role="MCA Student", content="The training refined not just my communication, but my overall personality. I now carry myself with confidence and clarity.", rating=5, image_url="https://ui-avatars.com/api/?name=Sai&background=d97706&color=fff"),
                Testimonial(name="Krishna", role="IBM Employee", content="I gained invaluable insights into managing workplace relations, stress, and behaviour. Thank you, Sharma Sir!", rating=5, image_url="https://ui-avatars.com/api/?name=Krishna&background=2a364b&color=fff")
            ])
        if not session.exec(select(Announcement)).first():
            session.add_all([
                Announcement(message="🚀 NEW BATCH: Weekend Spoken English batch starting this Saturday! Enroll now."),
                Announcement(message="⭐ PLACEMENT UPDATE: 15 students successfully placed in top MNCs this month."),
                Announcement(message="🎉 OFFER: Flat 20% off on all Corporate Leadership programs for a limited time.")
            ])

        if not session.exec(select(AdminConfig)).first():
            session.add(AdminConfig(password="admin123"))
        session.commit()

# --- 3. ROUTES ---
@app.get("/api/courses", response_model=List[Course])
def get_courses():
    with Session(engine) as session: return session.exec(select(Course)).all()

@app.post("/api/courses", response_model=Course)
def add_course(course: Course):
    with Session(engine) as session:
        session.add(course)
        session.commit()
        session.refresh(course)
        return course

@app.put("/api/courses/{course_id}", response_model=Course)
def update_course(course_id: int, updated_course: Course):
    with Session(engine) as session:
        db_course = session.get(Course, course_id)
        if db_course:
            for key, value in updated_course.dict(exclude_unset=True).items(): setattr(db_course, key, value)
            session.add(db_course)
            session.commit()
            session.refresh(db_course)
            return db_course

@app.delete("/api/courses/{course_id}")
def delete_course(course_id: int):
    with Session(engine) as session:
        course = session.get(Course, course_id)
        if course: session.delete(course); session.commit()
        return {"message": "Deleted"}

@app.get("/api/certificates", response_model=List[Certificate])
def get_certificates():
    with Session(engine) as session: return session.exec(select(Certificate)).all()

@app.post("/api/certificates", response_model=Certificate)
def issue_certificate(cert: Certificate):
    with Session(engine) as session:
        session.add(cert)
        session.commit()
        session.refresh(cert)
        return cert

@app.get("/api/certificates/verify/{cert_code}")
def verify_certificate(cert_code: str):
    with Session(engine) as session:
        cert = session.exec(select(Certificate).where(Certificate.cert_code == cert_code)).first()
        if not cert: raise HTTPException(status_code=404, detail="Invalid")
        return cert

@app.delete("/api/certificates/{cert_id}")
def delete_certificate(cert_id: int):
    with Session(engine) as session:
        cert = session.get(Certificate, cert_id)
        if cert: session.delete(cert); session.commit()
        return {"message": "Deleted"}

@app.get("/api/programs", response_model=List[Program])
def get_programs():
    with Session(engine) as session: return session.exec(select(Program)).all()

@app.post("/api/programs", response_model=Program)
def add_program(prog: Program):
    with Session(engine) as session:
        session.add(prog)
        session.commit()
        session.refresh(prog)
        return prog

@app.put("/api/programs/{prog_id}", response_model=Program)
def update_program(prog_id: int, updated_prog: Program):
    with Session(engine) as session:
        db_prog = session.get(Program, prog_id)
        if db_prog:
            for key, value in updated_prog.dict(exclude_unset=True).items(): setattr(db_prog, key, value)
            session.add(db_prog)
            session.commit()
            session.refresh(db_prog)
            return db_prog

@app.delete("/api/programs/{prog_id}")
def delete_program(prog_id: int):
    with Session(engine) as session:
        prog = session.get(Program, prog_id)
        if prog: session.delete(prog); session.commit()
        return {"message": "Deleted"}

@app.get("/api/testimonials", response_model=List[Testimonial])
def get_testimonials():
    with Session(engine) as session: return session.exec(select(Testimonial)).all()

@app.post("/api/testimonials", response_model=Testimonial)
def add_testimonial(test: Testimonial):
    with Session(engine) as session:
        session.add(test)
        session.commit()
        session.refresh(test)
        return test

@app.put("/api/testimonials/{test_id}", response_model=Testimonial)
def update_testimonial(test_id: int, updated_test: Testimonial):
    with Session(engine) as session:
        db_test = session.get(Testimonial, test_id)
        if db_test:
            for key, value in updated_test.dict(exclude_unset=True).items(): setattr(db_test, key, value)
            session.add(db_test)
            session.commit()
            session.refresh(db_test)
            return db_test

@app.delete("/api/testimonials/{test_id}")
def delete_testimonial(test_id: int):
    with Session(engine) as session:
        test = session.get(Testimonial, test_id)
        if test: session.delete(test); session.commit()
        return {"message": "Deleted"}
    

# --- 6. CAREERS & EMAIL ROUTES ---

def send_confirmation_email(name: str, email_to: str, phone: str, file_content: bytes, filename: str):
    sender_email = "mylavaramnagasaei@gmail.com"  # <--- UPDATE THIS
    sender_password = "yuqx lcnv vzhu iqqt"            # <--- UPDATE THIS
    
    message = MIMEMultipart("mixed")
    message["Subject"] = f"Application Received: {name} - Sharma Soft Skills"
    message["From"] = sender_email
    message["To"] = email_to
    
    # Premium HTML Email Template with Submitted Details
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 40px 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f4f4f5;">
        
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.05);">
            
            <div style="background-color: #111111; padding: 35px 30px; text-align: center;">
                <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 800; letter-spacing: -0.5px;">
                    SHARMA<br/>
                    <span style="color: #d97706; font-size: 16px; font-weight: 600; letter-spacing: 1px;">SOFT SKILLS</span>
                </h1>
            </div>

            <div style="padding: 40px 35px;">
                <h2 style="margin: 0 0 20px 0; color: #111111; font-size: 20px; font-weight: 700;">Application Received!</h2>
                
                <p style="margin: 0 0 25px 0; color: #444444; font-size: 16px; line-height: 1.6;">
                    Dear <strong>{name}</strong>, <br/><br/>
                    Thank you for showing interest in joining our institute. We have successfully received your application. Our HR team will start reviewing your profile immediately.
                </p>
                
                <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; margin-bottom: 25px;">
                    <h3 style="margin: 0 0 15px 0; color: #111111; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">Details Submitted</h3>
                    
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; color: #666666; font-size: 14px; font-weight: 600; width: 100px;">Name:</td>
                            <td style="padding: 8px 0; color: #111111; font-size: 15px; font-weight: 700;">{name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #666666; font-size: 14px; font-weight: 600;">Email:</td>
                            <td style="padding: 8px 0; color: #111111; font-size: 15px; font-weight: 700;">{email_to}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #666666; font-size: 14px; font-weight: 600;">Mobile:</td>
                            <td style="padding: 8px 0; color: #111111; font-size: 15px; font-weight: 700;">{phone}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #666666; font-size: 14px; font-weight: 600;">Resume:</td>
                            <td style="padding: 8px 0; color: #d97706; font-size: 15px; font-weight: 700;">Attached Inline Below ↓</td>
                        </tr>
                    </table>
                </div>
                
                <div style="background-color: rgba(217, 119, 6, 0.05); border-left: 4px solid #d97706; padding: 15px 20px; margin: 25px 0; border-radius: 0 8px 8px 0;">
                    <p style="margin: 0; color: #b45309; font-size: 14px; font-weight: 500; line-height: 1.5;">
                        We will respond to you as soon as possible, so please stay active on your provided phone number and email address.
                    </p>
                </div>
                
                <p style="margin: 0; color: #555555; font-size: 15px; line-height: 1.6;">
                    Best Regards,<br/>
                    <strong style="color: #111111;">Sharma Soft Skills Team</strong>
                </p>
            </div>

            <div style="background-color: #fafafa; padding: 25px; text-align: center; border-top: 1px solid #f0f0f0;">
                <p style="margin: 0; color: #888888; font-size: 12px;">
                    #107, Indulakeview Apartment, Sapthagiri Nagara, Bangalore – 560085<br/>
                    © 2026 Sharma Soft Skills. All rights reserved.
                </p>
            </div>

        </div>
    </body>
    </html>
    """
    
    # Attach the HTML body
    html_part = MIMEText(html, "html")
    message.attach(html_part)
    
    # Attach the PDF File as INLINE (forces Gmail/Apple Mail to preview it directly below the text)
    if file_content and filename:
        pdf_attachment = MIMEApplication(file_content, Name=filename)
        # Using "inline" instead of "attachment" encourages email clients to display the PDF visually
        pdf_attachment['Content-Disposition'] = f'inline; filename="{filename}"'
        message.attach(pdf_attachment)
    
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email_to, message.as_string())
        server.quit()
        print(f"Successfully sent styled email with inline PDF to {email_to}")
    except Exception as e:
        print(f"Error sending email: {e}")


@app.post("/api/careers/apply")
async def apply_career(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    resume: UploadFile = File(...)
):
    if not resume.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Read the file bytes directly into memory
    file_content = await resume.read()
    filename = resume.filename
    
    # Pass the phone number alongside everything else to the email function
    background_tasks.add_task(send_confirmation_email, name, email, phone, file_content, filename)
    
    return {"message": "Application received successfully"}

@app.get("/api/announcements", response_model=List[Announcement])
def get_announcements():
    with Session(engine) as session: return session.exec(select(Announcement)).all()

@app.post("/api/announcements", response_model=Announcement)
def add_announcement(ann: Announcement):
    with Session(engine) as session:
        session.add(ann)
        session.commit()
        session.refresh(ann)
        return ann

@app.delete("/api/announcements/{ann_id}")
def delete_announcement(ann_id: int):
    with Session(engine) as session:
        ann = session.get(Announcement, ann_id)
        if ann: session.delete(ann); session.commit()
        return {"message": "Deleted"}
    
# --- 7. ADMIN AUTHENTICATION & PASSWORD RESET ---

def send_reset_email(email_to: str, code: str):
    sender_email = "mylavaramnagasaei@gmail.com"  # <--- UPDATE THIS
    sender_password = "yuqx lcnv vzhu iqqt"            # <--- UPDATE THIS
    
    message = MIMEMultipart("alternative")
    message["Subject"] = "Admin Password Reset Code"
    message["From"] = sender_email
    message["To"] = email_to
    
    html = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
        <h2>Password Reset Request</h2>
        <p>You requested a password reset for the Admin Dashboard.</p>
        <p>Your 6-character reset code is:</p>
        <h1 style="color: #d97706; background: #fffbeb; padding: 10px 20px; display: inline-block; border-radius: 8px; border: 1px solid #fcd34d;">{code}</h1>
        <p>If you did not request this, please ignore this email.</p>
    </div>
    """
    message.attach(MIMEText(html, "html"))
    try:
        # 1. Connect to Port 587 (The modern, unblocked TLS port)
        server = smtplib.SMTP("smtp.gmail.com", 587)
        
        # 2. Identify ourselves to the server
        server.ehlo()
        
        # 3. Upgrade the connection to secure TLS
        server.starttls() 
        
        # 4. Login and send
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email_to, message.as_string())
        server.quit()
        
        print(f"SUCCESS: Reset email sent to {email_to}")
    except Exception as e:
        print(f"FAILED TO SEND EMAIL: {e}")

@app.post("/api/admin/login")
def admin_login(password: str = Form(...)):
    with Session(engine) as session:
        admin = session.exec(select(AdminConfig)).first()
        if admin and admin.password == password:
            return {"message": "Authenticated"}
        raise HTTPException(status_code=401, detail="Invalid password")

@app.post("/api/admin/forgot-password")
def forgot_password(background_tasks: BackgroundTasks):
    with Session(engine) as session:
        admin = session.exec(select(AdminConfig)).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        
        # Generate 6 char alphanumeric + special character code
        chars = string.ascii_uppercase + string.digits + "!@#$%"
        code = ''.join(random.choice(chars) for _ in range(6))
        
        admin.reset_code = code
        session.add(admin)
        session.commit()
        
        # Send to the institute's own email so the owner gets the code
        institute_email = "mylavaramnagasaei@gmail.com" # <--- UPDATE THIS
        background_tasks.add_task(send_reset_email, institute_email, code)
        return {"message": "Reset code sent"}

@app.post("/api/admin/reset-password")
def reset_password(code: str = Form(...), new_password: str = Form(...)):
    with Session(engine) as session:
        admin = session.exec(select(AdminConfig)).first()
        if admin and admin.reset_code == code:
            admin.password = new_password
            admin.reset_code = None # Clear code after use
            session.add(admin)
            session.commit()
            return {"message": "Password updated successfully"}
        raise HTTPException(status_code=400, detail="Invalid reset code")