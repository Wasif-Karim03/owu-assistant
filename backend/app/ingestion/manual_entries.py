"""Hardcoded knowledge about key OWU offices and resources.

These entries guarantee the assistant can answer core campus questions even
before any web scraping has run.  Update this file whenever office details
change (location, phone, hours).

Building locations verified against the OWU Offices & Services Directory.
"""

MANUAL_KNOWLEDGE_BASE: list[dict] = [
    {
        "title": "Student Accounts Office",
        "content": (
            "The Student Accounts Office handles tuition billing, payment plans, "
            "refunds, 1098-T tax forms, direct deposit setup, and account balances. "
            "Email: studentaccounts@owu.edu. Phone: (740) 368-3036.\n\n"
            "If you have a hold on your account, Student Accounts can explain why "
            "and help resolve it.\n\n"
            "Payments can be made online through the student portal, by mail, or in person. "
            "Payment plan enrollment opens each semester before the billing deadline.\n\n"
            "For 1098-T tax forms, contact the Student Accounts Office."
        ),
        "source_type": "manual",
        "metadata": {"category": "offices"},
    },
    {
        "title": "Career Connection (Career Services)",
        "content": (
            "Career Connection is OWU's career services office. It is located on "
            "the second floor of Slocum Hall, off the reading room (the room with "
            "the large stained glass ceiling).\n"
            "Email: careers@owu.edu. Phone: (740) 368-3152.\n"
            "Website: careers.owu.edu\n\n"
            "Drop-in hours: Monday–Thursday, 11 AM – 1 PM. Students can also "
            "schedule appointments through Handshake.\n\n"
            "Services include career counseling, résumé and cover letter reviews, "
            "mock interviews, internship and job search support, graduate school "
            "advising, and post-graduation planning.\n\n"
            "Career Connection uses a 'Discover-Prepare-Launch' model to help "
            "students explore career paths. Job and internship postings are "
            "available on Handshake, OWU's career platform.\n\n"
            "Note: Career Connection was formerly known as IOCP (Intersection of "
            "Career & Professional Development). It is now called Career Connection."
        ),
        "source_type": "manual",
        "metadata": {"category": "offices"},
    },
    {
        "title": "Registrar's Office (Office of the Registrar)",
        "content": (
            "The Office of the Registrar is located in University Hall, Room 007 "
            "(lower level).\n\n"
            "They handle course registration, add/drop, transcripts, degree audits, "
            "enrollment verification, graduation applications, and academic records.\n\n"
            "Important dates (registration windows, add/drop deadlines, commencement) "
            "are published on the academic calendar each semester.\n\n"
            "Transcripts can be ordered online through the National Student Clearinghouse."
        ),
        "source_type": "manual",
        "metadata": {"category": "offices"},
    },
    {
        "title": "Financial Aid Office",
        "content": (
            "The Financial Aid Office is located in Slocum Hall, Room 302.\n"
            "Email: financialaid@owu.edu. Phone: (740) 368-3050.\n\n"
            "They handle FAFSA processing, scholarships, grants, federal loans, "
            "work-study, merit aid, need-based aid, and satisfactory academic progress "
            "(SAP) reviews.\n\n"
            "Students should file the FAFSA by February 15 each year for priority aid. "
            "OWU's federal school code is 003100.\n\n"
            "The office can also help with appeals for special circumstances such as "
            "job loss, medical expenses, or changes in family income."
        ),
        "source_type": "manual",
        "metadata": {"category": "offices"},
    },
    {
        "title": "IT Help Desk (Information Technology)",
        "content": (
            "The IT Help Desk is located in R.W. Corns Building.\n"
            "Email: helpdesk@owu.edu.\n\n"
            "They handle Wi-Fi connectivity, email access, password resets, VPN setup, "
            "printing issues, classroom technology support, and software licensing.\n\n"
            "Students receive an OWU Google Workspace account (email, Drive, etc.) and "
            "can access campus Wi-Fi on the 'OWU-Secure' network with their university "
            "credentials."
        ),
        "source_type": "manual",
        "metadata": {"category": "offices"},
    },
    {
        "title": "Residential Life & Dining Services",
        "content": (
            "The Office of Residential Life is located in Hamilton-Williams Campus Center, "
            "Room 213. Phone: (740) 368-3135.\n\n"
            "They handle housing assignments, room changes, roommate conflicts, living "
            "learning communities, and residential hall policies.\n\n"
            "Room selection for returning students typically happens in March each year. "
            "First-year students receive their housing assignments over the summer.\n\n"
            "For maintenance or facility issues in residence halls, students should submit "
            "a work order through the housing portal.\n\n"
            "Dining options include The 1842 in Hamilton-Williams Campus Center, "
            "Smith Dining Hall, the Science Center Café, and the Bradford Milligan Market."
        ),
        "source_type": "manual",
        "metadata": {"category": "offices"},
    },
    {
        "title": "International Student Services",
        "content": (
            "International Student Services is located in Slocum Hall, Room 311.\n"
            "Email: international@owu.edu. Phone: (740) 368-3070.\n\n"
            "They support international students with visa guidance (F-1, J-1), "
            "I-20 processing, CPT and OPT employment authorization, cultural adjustment, "
            "and travel signatures.\n\n"
            "International students must maintain full-time enrollment and report any "
            "changes in address, major, or enrollment status to the office.\n\n"
            "OPT applications should be started 90 days before graduation. CPT requires "
            "an internship or practicum that is part of the academic program."
        ),
        "source_type": "manual",
        "metadata": {"category": "offices"},
    },
    {
        "title": "Student Health Services",
        "content": (
            "Student Health Services supports both physical and emotional health.\n\n"
            "Medical services include general illness treatment, immunization records, "
            "allergy shots, health screenings, and referrals to specialists.\n\n"
            "Students do not need insurance to visit the campus health center, though "
            "OWU offers a student health insurance plan for those who need coverage.\n\n"
            "For emergencies, call 911 or OWU Public Safety at (740) 368-2222."
        ),
        "source_type": "manual",
        "metadata": {"category": "offices"},
    },
    {
        "title": "Counseling Services",
        "content": (
            "Counseling Services helps with academic, personal, and professional "
            "development. They offer individual therapy, group sessions, crisis "
            "support, and referrals to community providers.\n\n"
            "For emergencies, call 911 or OWU Public Safety at (740) 368-2222."
        ),
        "source_type": "manual",
        "metadata": {"category": "offices"},
    },
    {
        "title": "Dean of Students Office",
        "content": (
            "The Dean of Students Office is located in Hamilton-Williams Campus Center.\n"
            "Email: deansoffice@owu.edu. Phone: (740) 368-3135.\n\n"
            "The Dean of Students serves as a general resource for student concerns "
            "that don't clearly fall under another office. They can help with academic "
            "difficulties, personal emergencies, medical withdrawals, student conduct, "
            "and connecting students to the right campus resources.\n\n"
            "If you're not sure where to go, the Dean of Students Office is a good "
            "starting point."
        ),
        "source_type": "manual",
        "metadata": {"category": "offices"},
    },
    {
        "title": "Department of Public Safety (Campus Safety)",
        "content": (
            "The Department of Public Safety is located in Welch Hall, Room 133.\n"
            "Phone: (740) 368-2222 (non-emergency). For emergencies call 911.\n\n"
            "Public Safety provides campus patrol, parking permits, lost and found, "
            "building lockouts, and the OWU Alert system for campus emergencies.\n\n"
            "They are available 24 hours a day, 7 days a week."
        ),
        "source_type": "manual",
        "metadata": {"category": "offices"},
    },
    {
        "title": "Admission Office",
        "content": (
            "The Admission Office is located in Slocum Hall.\n"
            "Email: owuadmit@owu.edu. Phone: (740) 368-3020 or (800) 922-8953.\n\n"
            "They handle undergraduate applications for first-year, transfer, "
            "and international students. Campus visits can be scheduled online.\n\n"
            "Office hours: Monday–Friday, 8:30 AM – 5:00 PM."
        ),
        "source_type": "manual",
        "metadata": {"category": "offices"},
    },
]
