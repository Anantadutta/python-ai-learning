"""
generate_policy_pdf.py
----------------------
Creates a realistic, 100+ page "Zenith Corp Employee Policy Handbook" PDF
so the RAG chatbot can be tested at a realistic scale.

The handbook contains:
  - Core policy chapters (HR, Leave, Expense/Travel, IT, Onboarding, Code of Conduct,
    Work-from-home, Performance, Exit) with SPECIFIC facts (numbers, deadlines, emails)
    that we can later ask the chatbot about.
  - Annexures (grade-wise allowance tables, office-wise holiday calendars,
    department onboarding checklists, form guides, a large FAQ) that add realistic bulk.

Run:  python generate_policy_pdf.py
Out:  data/Zenith_Corp_Employee_Handbook.pdf
"""

import os
import random
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, ListFlowable, ListItem)

random.seed(42)  # deterministic output
OUT_DIR = "data"
OUT_FILE = os.path.join(OUT_DIR, "Zenith_Corp_Employee_Handbook.pdf")

styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=18, spaceAfter=12,
                    textColor=colors.HexColor("#1F3A5F"))
H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13.5, spaceBefore=10,
                    spaceAfter=6, textColor=colors.HexColor("#1F3A5F"))
H3 = ParagraphStyle("H3", parent=styles["Heading3"], fontSize=11.5, spaceBefore=6,
                    spaceAfter=4)
BODY = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=10.5, leading=15,
                      spaceAfter=6)
SMALL = ParagraphStyle("Small", parent=BODY, fontSize=9, leading=12)

story = []


# ---------------------------------------------------------------- helpers
def h1(t): story.append(Paragraph(t, H1))
def h2(t): story.append(Paragraph(t, H2))
def h3(t): story.append(Paragraph(t, H3))
def p(t): story.append(Paragraph(t, BODY))
def br(): story.append(PageBreak())


def bullets(items):
    story.append(ListFlowable(
        [ListItem(Paragraph(i, BODY), leftIndent=12) for i in items],
        bulletType="bullet", start="-", leftIndent=14))


def numbered(items):
    story.append(ListFlowable(
        [ListItem(Paragraph(i, BODY)) for i in items],
        bulletType="1", leftIndent=16))


def table(rows, widths=None):
    t = Table(rows, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3A5F")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF2F7")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))


def standard_frame(policy, owner, sections):
    """Wraps a policy in the standard corporate structure used across Zenith documents:
    purpose, scope, definitions, responsibilities, the actual rules, exceptions,
    non-compliance and revision history."""
    code, name = policy
    h2(f"{code}.1 Purpose")
    p(f"This {name} sets out the principles, entitlements and procedures that apply to "
      f"all employees of Zenith Corp in relation to {name.lower().replace(' policy', '')}. "
      f"It is intended to ensure fair, consistent and transparent treatment of every employee "
      f"and to give managers a single reference point when making decisions. Where local law "
      f"provides a more favourable entitlement, the local law will prevail.")
    h2(f"{code}.2 Scope")
    p("This policy applies to all permanent full-time employees, permanent part-time employees "
      "(on a pro-rata basis unless stated otherwise) and fixed-term contract employees of Zenith "
      "Corp across all office locations in India. Interns, consultants and employees of third-party "
      "vendors are covered only where their contract explicitly refers to this policy.")
    h2(f"{code}.3 Policy Owner")
    p(f"The owner of this policy is the <b>{owner}</b>. Questions about the interpretation of this "
      f"policy should be raised first with the reporting manager and, if unresolved, with the "
      f"policy owner. The policy owner is responsible for reviewing this policy at least once "
      f"every twelve months.")
    for i, (title, paras) in enumerate(sections, start=4):
        h2(f"{code}.{i} {title}")
        for para in paras:
            if isinstance(para, list):
                bullets(para)
            elif isinstance(para, tuple) and para[0] == "num":
                numbered(para[1])
            elif isinstance(para, tuple) and para[0] == "table":
                table(para[1], para[2] if len(para) > 2 else None)
            else:
                p(para)
    n = len(sections) + 4
    h2(f"{code}.{n} Exceptions")
    p("Any exception to this policy must be approved in writing by the policy owner and the "
      "Chief People Officer. Exceptions are granted only in genuinely exceptional circumstances, "
      "are recorded in the employee's file, and do not set a precedent for future cases.")
    h2(f"{code}.{n+1} Non-Compliance")
    p("Failure to comply with this policy may lead to disciplinary action in line with the Zenith "
      "Corp Disciplinary Procedure (see the Code of Conduct chapter), up to and including "
      "termination of employment. Deliberate misuse of any entitlement under this policy is "
      "treated as misconduct.")
    h2(f"{code}.{n+2} Revision History")
    table([["Version", "Effective date", "Summary of changes", "Approved by"],
           ["1.0", "01-Apr-2022", "Initial release", owner],
           ["1.1", "01-Apr-2023", "Clarifications and process updates", owner],
           ["2.0", "01-Apr-2025", "Annual review; current version", "Chief People Officer"]],
          [2 * cm, 3 * cm, 7 * cm, 4.5 * cm])
    br()


# ---------------------------------------------------------------- cover + intro
story.append(Spacer(1, 6 * cm))
story.append(Paragraph("Zenith Corp", ParagraphStyle("c1", parent=H1, fontSize=34, alignment=1)))
story.append(Spacer(1, 0.6 * cm))
story.append(Paragraph("Employee Policy Handbook",
                       ParagraphStyle("c2", parent=H1, fontSize=22, alignment=1)))
story.append(Spacer(1, 0.4 * cm))
story.append(Paragraph("HR | Leave | Expense and Travel | IT | Onboarding | Conduct",
                       ParagraphStyle("c3", parent=BODY, alignment=1)))
story.append(Spacer(1, 0.4 * cm))
story.append(Paragraph("Version 2.0 - Effective 1 April 2025 - Internal use only",
                       ParagraphStyle("c4", parent=BODY, alignment=1)))
br()

h1("About This Handbook")
p("Welcome to Zenith Corp. This handbook brings together the company's HR policies, leave "
  "policy, expense and travel reimbursement rules, IT and information security guidelines, "
  "onboarding manual and code of conduct into a single reference. It replaces all earlier "
  "versions and all separately circulated policy documents.")
p("Zenith Corp is a mid-sized technology services company headquartered in Gurugram, with "
  "offices in Bengaluru, Pune, Hyderabad, Chennai, Mumbai, Noida, Kolkata, Ahmedabad and Kochi. "
  "The company employs approximately 1,800 people across engineering, sales, finance, human "
  "resources, operations and customer success.")
p("The HR Helpdesk can be reached at hr-helpdesk@zenithcorp.example or on internal extension "
  "2100, Monday to Friday, 9:30 AM to 6:30 PM IST. The IT Service Desk can be reached at "
  "itsupport@zenithcorp.example or on extension 4357 (HELP), 24 hours a day, 7 days a week.")
h2("Chapters")
numbered(["Chapter 1 - General HR Policy", "Chapter 2 - Leave Policy",
          "Chapter 3 - Working Hours, Attendance and Work From Home",
          "Chapter 4 - Expense Reimbursement Policy", "Chapter 5 - Travel Policy",
          "Chapter 6 - IT Usage and Information Security Guidelines",
          "Chapter 7 - Onboarding Manual", "Chapter 8 - Performance Management",
          "Chapter 9 - Code of Conduct and Disciplinary Procedure",
          "Chapter 10 - Separation and Exit",
          "Annexures A to J - Allowances, Holidays, Checklists, Forms, FAQ, Scenarios, Office Guides, IT SOPs, Glossary"])
br()

# ---------------------------------------------------------------- Chapter 1 HR
h1("Chapter 1 - General HR Policy")
standard_frame(("1", "General HR Policy"), "Head of Human Resources", [
    ("Employment Categories", [
        "Zenith Corp employs people in the following categories:",
        ["<b>Permanent full-time</b>: 40 hours per week, eligible for all benefits.",
         "<b>Permanent part-time</b>: 20 to 30 hours per week, benefits on a pro-rata basis.",
         "<b>Fixed-term contract</b>: engaged for a defined period of up to 24 months.",
         "<b>Interns</b>: engaged for 2 to 6 months; receive a monthly stipend, not a salary."],
    ]),
    ("Employee Grades", [
        "Every role is mapped to one of eight grades. Grades determine travel entitlements, "
        "approval limits and certain allowances.",
        ("table", [["Grade", "Typical titles", "Band"],
                   ["G1", "Associate, Trainee", "Junior"],
                   ["G2", "Senior Associate, Analyst", "Junior"],
                   ["G3", "Specialist, Engineer II", "Mid"],
                   ["G4", "Lead, Senior Engineer", "Mid"],
                   ["G5", "Manager, Principal Engineer", "Senior"],
                   ["G6", "Senior Manager, Architect", "Senior"],
                   ["G7", "Director", "Leadership"],
                   ["G8", "Vice President and above", "Leadership"]],
         [2.5 * cm, 9 * cm, 4 * cm]),
    ]),
    ("Probation Period", [
        "All new permanent employees serve a probation period of <b>six months</b> from their "
        "date of joining. The reporting manager may extend probation once, by up to three "
        "additional months, if performance or conduct expectations have not been met. The "
        "extension must be communicated in writing at least 15 days before the original "
        "probation end date.",
        "During probation, the notice period on either side is <b>15 days</b>. Earned leave "
        "accrues during probation but may only be used after probation is confirmed, except "
        "with the approval of the HR Business Partner.",
    ]),
    ("Salary and Payroll", [
        "Salaries are paid monthly on the <b>last working day of each month</b> by direct bank "
        "transfer. Payslips are published on the Zenith People Portal by the 2nd working day of "
        "the following month. Payroll inputs (new joiners, leave without pay, reimbursements) "
        "must reach Payroll by the <b>20th of the month</b> to be processed in that month's "
        "salary; inputs received later are processed in the following month.",
        "Salary advances of up to one month's net salary may be granted once in a 12-month "
        "period in cases of medical emergency, recovered in up to six equal monthly instalments.",
    ]),
    ("Benefits", [
        ["Group medical insurance of INR 5,00,000 per year covering the employee, spouse, up to "
         "two children and either parents or parents-in-law.",
         "Group term life insurance of three times annual fixed pay.",
         "Group personal accident insurance of INR 25,00,000.",
         "Annual health check-up for employees aged 30 and above.",
         "Employee Assistance Programme (EAP): free and confidential counselling, 24x7, "
         "on 1800-000-4321.",
         "Learning allowance of INR 25,000 per financial year for approved certifications and courses."],
    ]),
    ("Employee Referral Programme", [
        "Employees who refer a candidate who is hired and completes 90 days of service are "
        "eligible for a referral bonus: INR 25,000 for roles in grades G1 to G3, INR 50,000 for "
        "grades G4 to G5, and INR 75,000 for grades G6 and above. Referrals must be submitted "
        "through the Careers section of the Zenith People Portal. HR team members and hiring "
        "managers for the role are not eligible for the bonus.",
    ]),
    ("Grievance Redressal", [
        "Employees may raise a grievance with their reporting manager, their HR Business Partner, "
        "or confidentially by writing to grievance@zenithcorp.example. Every grievance is "
        "acknowledged within 2 working days and a resolution or status update is provided "
        "within 15 working days.",
        "Complaints of sexual harassment are handled by the Internal Committee (IC) under the "
        "POSH Act, 2013, and can be raised at ic@zenithcorp.example.",
    ]),
])

# ---------------------------------------------------------------- Chapter 2 Leave
h1("Chapter 2 - Leave Policy")
standard_frame(("2", "Leave Policy"), "Head of Human Resources", [
    ("Leave Year", [
        "The leave year runs from <b>1 January to 31 December</b>. All leave is applied for and "
        "approved on the Zenith People Portal under Leave, then Apply Leave.",
    ]),
    ("Summary of Leave Entitlements", [
        ("table", [["Leave type", "Entitlement per year", "Carry forward", "Encashable"],
                   ["Casual Leave (CL)", "12 days", "No", "No"],
                   ["Sick Leave (SL)", "10 days", "Yes, up to 30 days total", "No"],
                   ["Earned Leave (EL)", "18 days (1.5 days per month)", "Yes, up to 45 days total", "Yes, on exit"],
                   ["Maternity Leave", "26 weeks", "-", "-"],
                   ["Paternity Leave", "10 working days", "-", "-"],
                   ["Bereavement Leave", "5 working days per event", "-", "-"],
                   ["Marriage Leave", "5 working days (once)", "-", "-"],
                   ["Optional Holidays", "2 days from the list", "No", "No"]],
         [4.5 * cm, 5 * cm, 4 * cm, 3 * cm]),
    ]),
    ("Casual Leave", [
        "Every employee is entitled to <b>12 days of Casual Leave per calendar year</b>, credited "
        "in full on 1 January. Employees who join during the year receive casual leave on a "
        "pro-rata basis of one day for each full month remaining in the year.",
        "Casual leave is meant for short, unplanned personal needs. No more than <b>3 consecutive "
        "days</b> of casual leave may be taken at a time. Casual leave cannot be combined with "
        "earned leave in the same continuous absence. Unused casual leave lapses on 31 December "
        "and cannot be carried forward or encashed.",
        "Casual leave should be applied for at least one working day in advance where possible. "
        "In an emergency, the employee must inform the manager on the same day and apply on the "
        "portal within 2 working days of returning.",
    ]),
    ("Sick Leave", [
        "Employees are entitled to <b>10 days of Sick Leave per year</b>. Unused sick leave can be "
        "carried forward, subject to a maximum accumulated balance of 30 days.",
        "A medical certificate from a registered medical practitioner is required for sick leave "
        "of <b>more than 2 consecutive days</b>. The certificate must be uploaded to the portal "
        "within 3 working days of returning to work.",
    ]),
    ("Earned Leave", [
        "Earned leave (also called privilege leave) accrues at <b>1.5 days per completed month</b> of "
        "service, i.e. 18 days per year. It is intended for planned vacations and must be applied "
        "for at least <b>7 days in advance</b> for absences of 3 days or more.",
        "Up to <b>45 days</b> of earned leave may be accumulated. Any balance above 45 days on "
        "31 December lapses. Accumulated earned leave (up to 45 days) is encashed at the time of "
        "separation at the rate of the last drawn basic salary.",
    ]),
    ("Maternity Leave", [
        "Female employees are entitled to <b>26 weeks of paid maternity leave</b> for the first "
        "two children, of which up to 8 weeks may be taken before the expected date of delivery. "
        "For the third child onwards, maternity leave is 12 weeks. Employees adopting a child "
        "below the age of three months, and commissioning mothers, are entitled to 12 weeks.",
        "After maternity leave, employees may request to work from home for up to 3 months, "
        "subject to the nature of the role and manager approval.",
    ]),
    ("Paternity Leave", [
        "Male employees are entitled to <b>10 working days of paid paternity leave</b>, to be "
        "taken within 3 months of the birth or adoption of a child.",
    ]),
    ("Bereavement Leave", [
        "Employees may take up to <b>5 working days</b> of paid bereavement leave on the death "
        "of an immediate family member (spouse, child, parent, sibling, parent-in-law or grandparent).",
    ]),
    ("Leave Without Pay", [
        "Leave without pay (LWP) may be granted only after all applicable paid leave has been "
        "exhausted, for up to 30 days in a calendar year, with the approval of the reporting "
        "manager and the HR Business Partner. Unapproved absence is treated as LWP and may lead "
        "to disciplinary action.",
    ]),
    ("Public Holidays", [
        "Zenith Corp observes <b>10 fixed public holidays</b> per year, plus <b>2 optional "
        "holidays</b> that each employee may choose from the published list. Office-specific "
        "holiday calendars are published in December for the following year (see Annexure B).",
    ]),
    ("How to Apply for Leave", [
        ("num", ["Log in to the Zenith People Portal.",
                 "Go to Leave, then Apply Leave, and choose the leave type and dates.",
                 "Add a short reason and attach documents where required (e.g. medical certificate).",
                 "Submit. Your reporting manager receives an email and a portal notification.",
                 "The manager must approve or reject within 2 working days. Requests not acted on "
                 "within 2 working days are escalated automatically to the skip-level manager."]),
    ]),
])

# ---------------------------------------------------------------- Chapter 3 Hours/WFH
h1("Chapter 3 - Working Hours, Attendance and Work From Home")
standard_frame(("3", "Working Hours and Remote Work Policy"), "Head of Human Resources", [
    ("Standard Working Hours", [
        "The standard work week is Monday to Friday, 40 hours per week. Core collaboration hours "
        "are <b>11:00 AM to 4:00 PM IST</b>, during which all employees are expected to be "
        "available. Outside core hours, employees may flex their start and end times with their "
        "manager's agreement.",
    ]),
    ("Hybrid Work Model", [
        "Zenith Corp follows a hybrid model: employees work from the office a minimum of <b>3 days "
        "per week</b> (Tuesday, Wednesday and Thursday are the anchor days) and may work from home "
        "on the remaining days. Teams may agree on different anchor days with the approval of "
        "their department head.",
        "Employees may additionally request up to <b>12 days of full remote work per year</b> "
        "(for example, while visiting family) through the portal under Attendance, then Remote "
        "Work Request, at least 5 working days in advance.",
    ]),
    ("Home Office Setup", [
        "Employees receive a one-time home office allowance of <b>INR 15,000</b> in their first "
        "year for a chair, desk or other ergonomic equipment, reimbursed against bills through "
        "the expense portal. A monthly internet allowance of <b>INR 1,000</b> is paid with salary.",
    ]),
    ("Attendance", [
        "Office attendance is recorded by badge swipe. Employees who forget their badge must "
        "record attendance at the reception desk. Regularisation requests for missed swipes must "
        "be raised within 5 working days on the portal.",
    ]),
    ("Overtime and Compensatory Off", [
        "Employees in grades G1 to G3 who are asked to work on a weekend or public holiday are "
        "entitled to one day of compensatory off for each such day, to be availed within 60 days. "
        "Compensatory off requires prior written approval of the manager for the weekend work.",
    ]),
])

# ---------------------------------------------------------------- Chapter 4 Expense
h1("Chapter 4 - Expense Reimbursement Policy")
standard_frame(("4", "Expense Reimbursement Policy"), "Chief Financial Officer", [
    ("General Principles", [
        "Zenith Corp reimburses reasonable, necessary and actual expenses incurred by employees "
        "wholly for business purposes. Employees are expected to spend company money as carefully "
        "as they would spend their own.",
    ]),
    ("The Zenith Expense Portal (ZEP)", [
        "All reimbursement claims must be submitted through the <b>Zenith Expense Portal (ZEP)</b>, "
        "accessible from the Zenith People Portal home page. Paper and email claims are not accepted.",
    ]),
    ("Submission Deadline", [
        "Claims must be submitted within <b>30 days</b> of the date the expense was incurred (or "
        "within 30 days of returning from a trip). Claims submitted between 31 and 60 days require "
        "additional approval from the department head. Claims older than <b>60 days are not "
        "reimbursed</b>.",
    ]),
    ("Receipts", [
        "An original itemised receipt or tax invoice is required for every expense of <b>INR 500 "
        "or more</b>. For expenses below INR 500 where no receipt is available, a self-declaration "
        "may be submitted, subject to a maximum of INR 2,000 per month in self-declared expenses. "
        "Company GST details (printed on the ZEP home page) should be provided to vendors where "
        "possible so that the company can claim input tax credit.",
    ]),
    ("Approval Workflow", [
        ("num", ["Employee submits the claim with receipts on ZEP.",
                 "Reporting manager approves within 5 working days.",
                 "Finance team audits the claim within 5 working days of manager approval.",
                 "Approved claims are paid to the employee's salary account within "
                 "<b>10 working days</b> of Finance approval, in the next weekly payment run "
                 "(every Friday)."]),
        "Claims above <b>INR 50,000</b> also require approval from the department head.",
    ]),
    ("Reimbursable Expenses", [
        ["Business travel, accommodation and meals as per the Travel Policy (Chapter 5).",
         "Local conveyance for client meetings (taxi, auto, metro, or own vehicle at INR 12 per km "
         "for a car and INR 5 per km for a two-wheeler).",
         "Client entertainment, with prior approval, up to INR 3,000 per person.",
         "Mobile phone bills up to INR 1,500 per month for grades G4 and above, and for sales roles.",
         "Approved training and certification fees within the learning allowance.",
         "Home office allowance as described in Chapter 3."],
    ]),
    ("Non-Reimbursable Expenses", [
        ["Alcohol, except during approved client entertainment.",
         "Traffic fines, parking violations and penalties of any kind.",
         "Personal entertainment, such as in-room movies, spa or minibar.",
         "Laundry for trips shorter than 4 nights.",
         "Upgrades to travel class not permitted by the Travel Policy.",
         "Loss of personal belongings, and expenses of accompanying family members."],
    ]),
    ("Corporate Credit Card", [
        "Employees in grades G5 and above, and employees who travel more than 6 times a year, may "
        "apply for a Zenith corporate credit card. Card statements must be reconciled on ZEP by "
        "the 10th of each month. Personal use of the corporate card is strictly prohibited.",
    ]),
])

# ---------------------------------------------------------------- Chapter 5 Travel
h1("Chapter 5 - Travel Policy")
standard_frame(("5", "Travel Policy"), "Chief Financial Officer", [
    ("Travel Requests", [
        "All business travel must be approved in advance through a <b>Travel Request</b> on ZEP. "
        "Domestic travel requests should be raised at least <b>7 days</b> before travel and "
        "international travel at least <b>21 days</b> before travel. Bookings are made by the "
        "company's travel desk (travel@zenithcorp.example) after approval.",
    ]),
    ("Mode and Class of Travel", [
        ("table", [["Grade", "Air (domestic)", "Train", "International air"],
                   ["G1 - G3", "Economy", "AC 3-tier", "Economy"],
                   ["G4 - G5", "Economy", "AC 2-tier", "Economy (Premium Economy over 8 hrs)"],
                   ["G6 - G7", "Economy (Premium on request)", "AC 1st class", "Premium Economy"],
                   ["G8", "Business", "AC 1st class", "Business"]],
         [2.5 * cm, 4.5 * cm, 3 * cm, 6.5 * cm]),
        "Air travel is permitted where the train journey would exceed 8 hours.",
    ]),
    ("Accommodation", [
        "Employees should stay at company-empanelled hotels where available. Accommodation limits "
        "per night by city tier and grade are given in Annexure A.",
    ]),
    ("Daily Allowance (Per Diem)", [
        "A daily allowance covers meals and incidental expenses on business trips. It is paid "
        "without receipts at the rates in Annexure A. Where meals are provided by the host or "
        "hotel, the daily allowance is reduced by 25% per provided meal.",
    ]),
    ("How to Claim Travel Reimbursement", [
        ("num", ["Ensure your Travel Request was approved on ZEP before the trip.",
                 "Within 30 days of returning, open ZEP and choose New Claim, then Travel.",
                 "Link the claim to the approved Travel Request number.",
                 "Add each expense line (hotel, local taxi, meals if not claiming per diem) and "
                 "upload receipts for items of INR 500 or more.",
                 "Submit. The claim follows the approval workflow in Chapter 4 and is paid within "
                 "10 working days of Finance approval."]),
    ]),
    ("Travel Advance", [
        "A travel advance of up to 75% of the estimated trip cost may be requested on ZEP. "
        "Advances must be settled within 15 days of returning; unsettled advances are recovered "
        "from salary.",
    ]),
    ("Safety and Insurance", [
        "All employees on business travel are covered by the company's travel insurance. For "
        "international travel, employees must register their itinerary with the travel desk and "
        "save the 24x7 travel assistance number, +91-124-000-9911.",
    ]),
])

# ---------------------------------------------------------------- Chapter 6 IT
h1("Chapter 6 - IT Usage and Information Security Guidelines")
standard_frame(("6", "IT and Information Security Policy"), "Chief Information Security Officer", [
    ("Acceptable Use", [
        "Company devices, networks and accounts are provided for business use. Limited personal use "
        "is permitted if it does not interfere with work, consume excessive resources or breach "
        "any law or company policy. Installing unapproved software is not permitted; approved "
        "software is available in the <b>Zenith Software Center</b> application.",
    ]),
    ("Passwords and Authentication", [
        ["Passwords must be at least <b>12 characters</b> long and include upper-case, lower-case, "
         "a number and a special character.",
         "Passwords must be changed every <b>90 days</b>; the last 10 passwords cannot be reused.",
         "Accounts are locked after <b>5 failed login attempts</b> and unlock automatically after "
         "30 minutes, or immediately through the IT Service Desk.",
         "Multi-factor authentication (MFA) through the Zenith Authenticator app is mandatory for "
         "email, VPN and all business applications.",
         "Passwords must never be shared, including with IT staff."],
    ]),
    ("Laptops and Devices", [
        "Every employee is issued a company laptop on day one. Laptops are encrypted, managed "
        "centrally and must be kept updated; security updates are installed automatically and "
        "the laptop must be restarted within 3 days of an update prompt.",
        "A lost or stolen laptop must be reported to the IT Service Desk within <b>2 hours</b> and "
        "to the police within 24 hours; a copy of the police report must be sent to IT. The "
        "employee may be asked to bear 25% of the depreciated value of the device if loss "
        "results from negligence.",
        "Hardware is refreshed every <b>4 years</b>. Requests for additional hardware (monitor, "
        "keyboard, headset) are raised on the IT portal under Request Hardware.",
    ]),
    ("VPN and Remote Access", [
        "When working outside the office, employees must connect through the <b>Zenith VPN</b> "
        "(GlobalConnect client) to access internal systems. Public Wi-Fi may be used only when "
        "connected to the VPN.",
    ]),
    ("Email and Communication", [
        "Company email must not be auto-forwarded to personal accounts. Confidential information "
        "must be shared only through company-approved tools (Zenith Mail, Zenith Drive, and the "
        "company chat workspace). Employees must not use personal messaging apps for sharing "
        "customer data.",
    ]),
    ("Data Classification", [
        ("table", [["Class", "Examples", "Handling"],
                   ["Public", "Marketing material, website content", "No restrictions"],
                   ["Internal", "Policies, org charts, internal announcements", "Share only within Zenith"],
                   ["Confidential", "Customer data, financials, contracts", "Need-to-know; encrypt in transit"],
                   ["Restricted", "Salary data, source code, security keys", "Named access only; no external sharing"]],
         [3 * cm, 6.5 * cm, 7 * cm]),
    ]),
    ("Reporting Security Incidents", [
        "Suspected phishing emails must be reported with the <b>Report Phishing</b> button in "
        "Zenith Mail. Any other security incident (malware, data leak, suspicious access) must be "
        "reported to <b>security@zenithcorp.example</b> or extension 4357 within <b>1 hour</b> of "
        "discovery. Employees will not be penalised for reporting in good faith.",
    ]),
    ("Getting IT Help", [
        "Raise a ticket on the IT portal (it.zenithcorp.example) or call extension 4357. Ticket "
        "priorities and target resolution times are: P1 (business down) 4 hours; P2 (major "
        "impact) 1 working day; P3 (minor issue) 3 working days; P4 (request) 5 working days.",
    ]),
])

# ---------------------------------------------------------------- Chapter 7 Onboarding
h1("Chapter 7 - Onboarding Manual")
standard_frame(("7", "Onboarding Manual"), "Head of Talent and Onboarding", [
    ("Before Day One", [
        "After accepting the offer, new joiners receive a link to the <b>Zenith Pre-boarding "
        "Portal</b>, where they must upload the following at least 7 days before joining: "
        "identity proof, address proof, PAN card, educational certificates, relieving letters "
        "from previous employers, a passport-size photograph and bank account details.",
    ]),
    ("Day One", [
        ("num", ["Report to the office reception at 9:30 AM with a government photo ID.",
                 "Collect your access badge and laptop from the IT and Facilities desk.",
                 "Attend the Welcome Induction (9:45 AM to 1:00 PM) run by HR.",
                 "Lunch with your manager and assigned onboarding buddy.",
                 "Afternoon: IT setup session, MFA enrolment and email activation."]),
    ]),
    ("Onboarding Buddy", [
        "Each new joiner is paired with an onboarding buddy from the same team for the first "
        "<b>90 days</b>. The buddy helps with informal questions, introductions and settling in, "
        "and meets the new joiner at least once a week during the first month.",
    ]),
    ("Mandatory Trainings", [
        "The following e-learning modules on the Zenith Learning Hub must be completed within the "
        "<b>first 30 days</b>:",
        ["Code of Conduct and Ethics", "Information Security Awareness",
         "Prevention of Sexual Harassment (POSH)", "Data Privacy Essentials",
         "Anti-Bribery and Anti-Corruption"],
        "Failure to complete mandatory training within 30 days may delay probation confirmation.",
    ]),
    ("30-60-90 Day Plan", [
        "Within the first week, the manager and new joiner agree on a 30-60-90 day plan: learning "
        "goals for the first 30 days, first contributions by day 60, and independent ownership of "
        "defined work by day 90. Check-ins are held at the end of each 30-day period.",
    ]),
    ("Probation Review", [
        "A formal probation review is held in the <b>fifth month</b> of employment. The manager "
        "records a recommendation (confirm, extend or not confirm) on the portal, and HR issues a "
        "confirmation letter by the end of the sixth month.",
    ]),
])

# ---------------------------------------------------------------- Chapter 8 Performance
h1("Chapter 8 - Performance Management")
standard_frame(("8", "Performance Management Policy"), "Head of Human Resources", [
    ("Performance Cycle", [
        "Zenith Corp runs an annual performance cycle aligned with the financial year (April to "
        "March), with a mid-year check-in in October and the annual review in April. Goals are set "
        "on the portal by <b>30 April</b> each year.",
    ]),
    ("Rating Scale", [
        ("table", [["Rating", "Label", "Description"],
                   ["5", "Exceptional", "Consistently exceeds all expectations"],
                   ["4", "Exceeds", "Frequently exceeds expectations"],
                   ["3", "Meets", "Fully meets expectations"],
                   ["2", "Partially meets", "Meets some expectations; improvement needed"],
                   ["1", "Does not meet", "Does not meet expectations"]],
         [2 * cm, 4 * cm, 10.5 * cm]),
    ]),
    ("Increments and Promotions", [
        "Salary increments are effective from <b>1 July</b> each year. Promotions are considered "
        "twice a year, in April and October. Employees must have spent at least 18 months in "
        "their current grade to be eligible for promotion, unless rated 5 in the latest cycle.",
    ]),
    ("Performance Improvement Plan", [
        "Employees rated 1, or rated 2 in two consecutive cycles, may be placed on a Performance "
        "Improvement Plan (PIP) of <b>60 days</b> with clear goals and fortnightly reviews.",
    ]),
])

# ---------------------------------------------------------------- Chapter 9 Conduct
h1("Chapter 9 - Code of Conduct and Disciplinary Procedure")
standard_frame(("9", "Code of Conduct"), "Chief People Officer", [
    ("Core Expectations", [
        ["Act with integrity and honesty in all dealings.",
         "Treat colleagues, customers and partners with respect and dignity.",
         "Avoid conflicts of interest and declare any that arise.",
         "Protect company assets and confidential information.",
         "Comply with all applicable laws and company policies."],
    ]),
    ("Gifts and Hospitality", [
        "Employees may accept gifts of nominal value (up to <b>INR 2,000</b>) from business "
        "partners. Gifts above this value must be declared to compliance@zenithcorp.example "
        "within 5 days and may need to be returned. Cash or cash equivalents must never be accepted.",
    ]),
    ("Outside Employment", [
        "Employees must not take up any other paid employment or business activity without the "
        "prior written approval of HR. Unpaid community or academic activities are permitted if "
        "they do not conflict with Zenith's interests.",
    ]),
    ("Whistleblower Policy", [
        "Concerns about fraud, bribery or unethical behaviour can be raised anonymously through "
        "the Ethics Hotline at ethics@zenithcorp.example or 1800-000-7788. Retaliation against "
        "a whistleblower is itself a serious disciplinary offence.",
    ]),
    ("Disciplinary Procedure", [
        ("num", ["Informal discussion with the manager for minor issues.",
                 "Written warning, recorded on file for 12 months.",
                 "Final written warning, recorded on file for 24 months.",
                 "Termination of employment."]),
        "Gross misconduct (for example fraud, violence, harassment or serious data breach) may "
        "lead to immediate suspension and termination without prior warnings, following an inquiry.",
    ]),
])

# ---------------------------------------------------------------- Chapter 10 Exit
h1("Chapter 10 - Separation and Exit")
standard_frame(("10", "Separation Policy"), "Head of Human Resources", [
    ("Notice Period", [
        ("table", [["Status / Grade", "Notice period"],
                   ["On probation (any grade)", "15 days"],
                   ["Confirmed, G1 - G3", "30 days"],
                   ["Confirmed, G4 - G6", "60 days"],
                   ["Confirmed, G7 - G8", "90 days"]],
         [8 * cm, 8 * cm]),
        "The notice period may be shortened by mutual agreement, or bought out against the "
        "unserved days of basic salary.",
    ]),
    ("Resignation Process", [
        "Resignations are submitted on the portal under Separation, then Resign. The manager holds "
        "a conversation within 3 working days. Earned leave may not be used to adjust the notice "
        "period without the manager's approval.",
    ]),
    ("Exit Clearance and Full and Final Settlement", [
        "The departing employee must return the laptop, access badge, corporate card and any other "
        "company property on the last working day. Full and final settlement, including earned "
        "leave encashment and pending reimbursements, is processed within <b>45 days</b> of the "
        "last working day. The relieving letter and experience letter are issued along with the "
        "settlement.",
    ]),
])

# ---------------------------------------------------------------- Annexure A allowances
h1("Annexure A - Accommodation and Daily Allowance Limits")
p("City tiers: <b>Tier 1</b> - Mumbai, Delhi NCR (including Gurugram and Noida), Bengaluru, "
  "Chennai, Hyderabad, Kolkata, Pune. <b>Tier 2</b> - Ahmedabad, Kochi, Jaipur, Chandigarh, "
  "Lucknow, Indore, Coimbatore, Nagpur, Bhubaneswar, Visakhapatnam. <b>Tier 3</b> - all other "
  "cities in India. All amounts are in INR per night (accommodation) or per day (daily allowance).")
grades = ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"]
base_hotel = {"Tier 1": 4000, "Tier 2": 3000, "Tier 3": 2200}
base_da = {"Tier 1": 1200, "Tier 2": 900, "Tier 3": 700}
for tier in ["Tier 1", "Tier 2", "Tier 3"]:
    h2(f"A.{['Tier 1','Tier 2','Tier 3'].index(tier)+1} Domestic travel - {tier} cities")
    rows = [["Grade", "Hotel limit / night", "Daily allowance", "Local conveyance / day"]]
    for i, g in enumerate(grades):
        hotel = int(base_hotel[tier] * (1 + 0.25 * i) // 100 * 100)
        da = int(base_da[tier] * (1 + 0.15 * i) // 50 * 50)
        conv = 800 + 150 * i if tier == "Tier 1" else 600 + 100 * i
        rows.append([g, f"INR {hotel:,}", f"INR {da:,}", f"INR {conv:,}"])
    table(rows, [3 * cm, 4.5 * cm, 4.5 * cm, 4.5 * cm])
    p(f"Notes for {tier}: amounts exclude GST. Where the hotel limit is exceeded because no "
      f"empanelled property is available, the travel desk must record the reason and the "
      f"department head must approve the excess before check-in.")
br()
h2("A.4 International travel - daily allowance (USD per day)")
countries = [("United States", 90, 110), ("United Kingdom", 85, 105), ("Germany", 80, 100),
             ("France", 80, 100), ("Singapore", 75, 95), ("UAE", 70, 90), ("Japan", 85, 105),
             ("Australia", 80, 100), ("Canada", 80, 100), ("Netherlands", 80, 100),
             ("Malaysia", 55, 70), ("Thailand", 50, 65), ("South Africa", 55, 70),
             ("Saudi Arabia", 70, 90), ("Other countries", 60, 80)]
rows = [["Country", "G1 - G5", "G6 - G8", "Hotel cap (USD/night)"]]
for c, a, b in countries:
    rows.append([c, f"USD {a}", f"USD {b}", f"USD {a * 2 + 40}"])
table(rows, [5 * cm, 3.5 * cm, 3.5 * cm, 4.5 * cm])
br()

# ---------------------------------------------------------------- Annexure B holidays
h1("Annexure B - Office Holiday Calendars 2026")
p("Every office observes 10 fixed holidays. In addition, each employee may select 2 optional "
  "holidays from the list for their office. Optional holidays must be selected on the portal "
  "by 31 January.")
common = [("01-Jan-2026", "New Year's Day"), ("26-Jan-2026", "Republic Day"),
          ("04-Mar-2026", "Holi"), ("01-May-2026", "May Day / Maharashtra Day"),
          ("15-Aug-2026", "Independence Day"), ("02-Oct-2026", "Gandhi Jayanti"),
          ("20-Oct-2026", "Dussehra"), ("09-Nov-2026", "Diwali"),
          ("25-Dec-2026", "Christmas")]
regional = {"Gurugram": "Guru Nanak Jayanti (24-Nov-2026)", "Noida": "Guru Nanak Jayanti (24-Nov-2026)",
            "Bengaluru": "Karnataka Rajyotsava (01-Nov-2026)", "Pune": "Gudi Padwa (19-Mar-2026)",
            "Mumbai": "Ganesh Chaturthi (14-Sep-2026)", "Hyderabad": "Telangana Formation Day (02-Jun-2026)",
            "Chennai": "Pongal (15-Jan-2026)", "Kolkata": "Durga Puja - Saptami (18-Oct-2026)",
            "Ahmedabad": "Uttarayan (14-Jan-2026)", "Kochi": "Onam (26-Aug-2026)"}
optional = ["Makar Sankranti (14-Jan-2026)", "Maha Shivaratri (15-Feb-2026)",
            "Id-ul-Fitr (21-Mar-2026)", "Good Friday (03-Apr-2026)", "Buddha Purnima (01-May-2026)",
            "Muharram (26-Jun-2026)", "Raksha Bandhan (28-Aug-2026)", "Janmashtami (04-Sep-2026)",
            "Bhai Dooj (11-Nov-2026)", "Christmas Eve (24-Dec-2026)"]
addresses = {"Gurugram": "Tower B, Cyber Park, Sector 39, Gurugram (Headquarters)",
             "Noida": "Plot 12, Sector 62, Noida", "Bengaluru": "Level 6, Orion Tech Park, Outer Ring Road",
             "Pune": "Wing C, Riverside Business Bay, Kharadi", "Mumbai": "12th Floor, Harbour Point, BKC",
             "Hyderabad": "Block 3, Madhapur Knowledge City", "Chennai": "Olympia Grande, OMR, Perungudi",
             "Kolkata": "Sector V, Salt Lake, Tower 2", "Ahmedabad": "GIFT City, Block 11",
             "Kochi": "Infopark Phase 2, Kakkanad"}
for office in regional:
    h2(f"B - {office} Office")
    p(f"Address: {addresses[office]}. Facilities contact: facilities.{office.lower()}@zenithcorp.example.")
    rows = [["Date", "Holiday", "Type"]] + [[d, n, "Fixed"] for d, n in common]
    name, date = regional[office].split(" (")
    rows.append([date.rstrip(")"), name, "Fixed (regional)"])
    table(rows, [4 * cm, 8.5 * cm, 4 * cm])
    p("Optional holidays for this office (choose any 2): " + "; ".join(optional) + ".")
    p("Office timings: the office is open from 8:00 AM to 9:00 PM on working days. Cafeteria "
      "service runs from 8:30 AM to 7:30 PM. Visitors must be pre-registered by the host "
      "employee on the Visitor Management System at least 4 hours in advance.")
    br()

# ---------------------------------------------------------------- Annexure C department checklists
h1("Annexure C - Department Onboarding Checklists")
depts = {
    "Engineering": ["GitHub Enterprise access", "Jira and Confluence", "CI/CD pipeline read access",
                    "Secure coding training (within 45 days)", "Development environment setup guide"],
    "Sales": ["CRM (Salesforce) licence", "Product pitch certification (within 60 days)",
              "Sales commission plan briefing", "Corporate mobile SIM", "Client meeting shadowing: 5 meetings"],
    "Finance": ["ERP (SAP) access", "Delegation of authority matrix review", "Month-end close calendar",
                "Segregation of duties briefing", "Audit and controls training"],
    "Human Resources": ["HRMS admin access", "POSH Internal Committee briefing", "Payroll calendar",
                        "Employee data privacy training", "Grievance handling SOP"],
    "Customer Success": ["Ticketing tool (Zendesk) access", "Product certification level 1",
                         "SLA matrix briefing", "Escalation matrix", "Shadow 10 customer calls"],
    "Operations": ["Vendor management system access", "Procurement policy briefing",
                   "Asset management tool", "Facility safety training", "Business continuity plan review"],
    "Marketing": ["Brand guidelines", "CMS and website admin", "Marketing automation tool",
                  "Social media policy briefing", "Campaign approval workflow"],
    "Legal and Compliance": ["Contract management system", "Regulatory calendar",
                             "Anti-bribery refresher", "Data protection officer briefing", "Litigation register"],
    "Information Security": ["SIEM console access", "Incident response runbook",
                             "On-call rotation briefing", "Vulnerability management SOP", "Privileged access review"],
    "Product Management": ["Roadmap tool access", "Customer research repository",
                           "Release governance process", "Analytics dashboards", "Stakeholder map"],
    "Data and Analytics": ["Data warehouse read access", "Data governance training",
                           "BI tool licence", "PII handling guidelines", "Model review board process"],
    "Administration": ["Travel desk tools", "Facilities ticketing", "Front office SOP",
                       "Transport roster system", "Emergency evacuation plan"],
}
for d, items in depts.items():
    h2(f"C - {d}")
    p(f"In addition to the company-wide onboarding steps in Chapter 7, new joiners in {d} "
      f"complete the following department-specific steps. The department onboarding coordinator "
      f"tracks completion and reports status to the Head of Talent and Onboarding at the end of "
      f"week 4.")
    rows = [["#", "Item", "Owner", "Due by"]]
    owners = ["IT Service Desk", "Reporting manager", "Onboarding buddy", "Department coordinator", "HR"]
    for i, it in enumerate(items, 1):
        rows.append([str(i), it, owners[(i - 1) % len(owners)], f"Day {[1, 3, 7, 15, 30][i - 1]}"])
    table(rows, [1 * cm, 8.5 * cm, 4.5 * cm, 2.5 * cm])
    p(f"Week-by-week expectations for {d}: in week 1 the new joiner completes system access and "
      f"introductions; in week 2 they review the team's current priorities and documentation; in "
      f"week 3 they take on a first small task with support; and in week 4 they present their "
      f"30-day learnings to the manager. Any access requests still pending after day 7 should be "
      f"escalated to the IT Service Desk as P3 tickets.")
    br()

# ---------------------------------------------------------------- Annexure D forms
h1("Annexure D - Guide to Common Forms")
forms = [
    ("HR-01 Leave Application", "Zenith People Portal > Leave", "Reporting manager"),
    ("HR-02 Leave Regularisation", "Zenith People Portal > Attendance", "Reporting manager"),
    ("HR-03 Address Change", "Zenith People Portal > My Profile", "HR Operations"),
    ("HR-04 Bank Account Change", "Zenith People Portal > My Profile", "Payroll"),
    ("HR-05 Salary Advance Request", "Zenith People Portal > Payroll", "HR Business Partner and Finance"),
    ("HR-06 Employment Verification Letter", "Zenith People Portal > Letters", "HR Operations"),
    ("HR-07 Internal Job Posting Application", "Zenith People Portal > Careers", "Talent Acquisition"),
    ("HR-08 Resignation", "Zenith People Portal > Separation", "Reporting manager and HR"),
    ("FIN-01 Expense Claim", "Zenith Expense Portal", "Reporting manager and Finance"),
    ("FIN-02 Travel Request", "Zenith Expense Portal", "Reporting manager"),
    ("FIN-03 Travel Advance", "Zenith Expense Portal", "Reporting manager and Finance"),
    ("FIN-04 Corporate Card Application", "Zenith Expense Portal", "Department head and Finance"),
    ("FIN-05 Investment Declaration (Tax)", "Zenith People Portal > Payroll", "Payroll"),
    ("IT-01 Hardware Request", "IT portal > Request Hardware", "IT Service Desk"),
    ("IT-02 Software Request", "Zenith Software Center", "IT Service Desk"),
    ("IT-03 Access Request", "IT portal > Access", "Application owner"),
    ("IT-04 Lost Device Report", "IT portal > Report Incident", "IT Security"),
    ("IT-05 VPN Access", "IT portal > Access", "IT Service Desk"),
    ("ADM-01 Visitor Registration", "Visitor Management System", "Host employee"),
    ("ADM-02 Transport Request", "Admin portal > Transport", "Administration"),
]
for code, where, approver in forms:
    h3(code)
    p(f"<b>Where to find it:</b> {where}. <b>Approved by:</b> {approver}. "
      f"<b>Typical turnaround:</b> {random.choice([1, 2, 3, 5])} working days.")
    p("Fill in every mandatory field marked with an asterisk, attach supporting documents in PDF "
      "or JPG format (maximum 5 MB each), and review the summary page before submitting. You will "
      "receive an email confirmation with a reference number, which should be quoted in any "
      "follow-up with the relevant team. Rejected forms can be corrected and resubmitted from "
      "the My Requests page.")
br()

# ---------------------------------------------------------------- Annexure E FAQ
h1("Annexure E - Frequently Asked Questions")
faq = [
    ("Leave", [
        ("How many casual leaves do I get per year?", "12 days per calendar year, credited on 1 January, pro-rated for mid-year joiners. Unused casual leave lapses on 31 December."),
        ("Can I carry forward casual leave?", "No. Casual leave cannot be carried forward or encashed."),
        ("How many sick leaves do I get?", "10 days per year, which can be accumulated up to 30 days."),
        ("When do I need a medical certificate?", "For sick leave of more than 2 consecutive days, uploaded within 3 working days of return."),
        ("How much earned leave can I accumulate?", "Up to 45 days. Balances above 45 on 31 December lapse."),
        ("Is earned leave encashed?", "Yes, up to 45 days, at the time of separation, at the last drawn basic salary."),
        ("How long is maternity leave?", "26 weeks for the first two children; 12 weeks from the third child onwards."),
        ("How long is paternity leave?", "10 working days, to be taken within 3 months of birth or adoption."),
        ("What if my manager does not approve my leave?", "Requests not acted on within 2 working days are escalated automatically to the skip-level manager."),
        ("Can I take casual leave for a week?", "No. A maximum of 3 consecutive days of casual leave may be taken at a time."),
        ("How many optional holidays can I take?", "2 per year, chosen from your office's list by 31 January."),
    ]),
    ("Expenses and Travel", [
        ("How do I claim travel reimbursement?", "Raise a new Travel claim on ZEP within 30 days of return, link it to the approved Travel Request, add expenses with receipts for items of INR 500 or more, and submit."),
        ("What is the deadline for submitting expense claims?", "30 days. Between 31 and 60 days needs department head approval; after 60 days claims are not reimbursed."),
        ("When will I get my reimbursement?", "Within 10 working days of Finance approval, in the Friday payment run."),
        ("Do I need receipts for small expenses?", "Receipts are required for INR 500 and above. Below that, a self-declaration is accepted up to INR 2,000 per month."),
        ("How much is the mileage rate for my car?", "INR 12 per km for a car and INR 5 per km for a two-wheeler."),
        ("Can I get a travel advance?", "Yes, up to 75% of the estimated cost, settled within 15 days of return."),
        ("How early should I raise a travel request?", "7 days before domestic travel and 21 days before international travel."),
        ("Is alcohol reimbursable?", "Only during approved client entertainment."),
        ("Who approves claims above INR 50,000?", "The department head, in addition to the reporting manager and Finance."),
    ]),
    ("IT", [
        ("How often must I change my password?", "Every 90 days. Passwords must be at least 12 characters."),
        ("My account is locked, what do I do?", "It unlocks automatically after 30 minutes, or call the IT Service Desk on extension 4357."),
        ("I lost my laptop, what should I do?", "Report it to the IT Service Desk within 2 hours and file a police report within 24 hours."),
        ("How do I report a phishing email?", "Use the Report Phishing button in Zenith Mail."),
        ("Can I install software on my laptop?", "Only approved software from the Zenith Software Center."),
        ("When will my laptop be replaced?", "Hardware is refreshed every 4 years."),
    ]),
    ("Onboarding and General", [
        ("What time should I report on my first day?", "9:30 AM at the office reception with a government photo ID."),
        ("How long is the probation period?", "Six months, extendable once by up to three months."),
        ("Which trainings are mandatory?", "Code of Conduct, Information Security Awareness, POSH, Data Privacy Essentials and Anti-Bribery, within 30 days."),
        ("When is salary paid?", "On the last working day of each month."),
        ("How many days must I work from the office?", "At least 3 days per week, with Tuesday to Thursday as anchor days."),
        ("What is the notice period?", "15 days on probation; 30, 60 or 90 days after confirmation depending on grade."),
        ("What is the referral bonus?", "INR 25,000 for G1-G3, INR 50,000 for G4-G5 and INR 75,000 for G6 and above, after 90 days of the hire's service."),
        ("What is the learning allowance?", "INR 25,000 per financial year for approved courses and certifications."),
    ]),
]
for section, qas in faq:
    h2(f"E - {section}")
    for q, a in qas:
        h3("Q: " + q)
        p("A: " + a + " Refer to the relevant chapter of this handbook for full details and exceptions.")
br()

# ---------------------------------------------------------------- Annexure G worked scenarios
h1("Annexure G - Worked Scenarios and Policy Interpretations")
p("The scenarios below show how the policies in this handbook are applied in practice. They are "
  "illustrative; the chapter text always prevails over a scenario.")
names = ["Aarav", "Priya", "Rohan", "Sneha", "Vikram", "Ananya", "Karthik", "Meera", "Arjun",
         "Divya", "Farhan", "Ishita", "Nikhil", "Pooja", "Rahul", "Tanvi", "Siddharth", "Kavya"]
cities_t = [("Mumbai", "Tier 1"), ("Jaipur", "Tier 2"), ("Bengaluru", "Tier 1"),
            ("Indore", "Tier 2"), ("Mysuru", "Tier 3"), ("Chennai", "Tier 1"),
            ("Lucknow", "Tier 2"), ("Nashik", "Tier 3")]
scenario_no = 1
for i in range(16):  # travel claim scenarios with computed numbers
    n = names[i % len(names)]
    g = grades[i % 6]
    gi = grades.index(g)
    city, tier = cities_t[i % len(cities_t)]
    nights = 2 + i % 4
    hotel = int(base_hotel[tier] * (1 + 0.25 * gi) // 100 * 100)
    da = int(base_da[tier] * (1 + 0.15 * gi) // 50 * 50)
    actual = hotel + random.choice([-600, -300, 0, 400, 900])
    allowed = min(actual, hotel)
    total = allowed * nights + da * (nights + 1)
    h2(f"G.{scenario_no} Travel claim - {n} ({g}) to {city}")
    p(f"{n}, a grade {g} employee based in Gurugram, travelled to {city} ({tier}) for a client "
      f"workshop for {nights} nights. The hotel charged INR {actual:,} per night. The {tier} hotel "
      f"limit for {g} is INR {hotel:,} per night and the daily allowance is INR {da:,} per day.")
    p(f"<b>Outcome:</b> the reimbursable hotel amount is INR {allowed:,} per night"
      f"{' (the excess over the limit is borne by the employee unless approved in advance by the department head)' if actual > hotel else ''}. "
      f"Daily allowance is paid for {nights + 1} days (travel days included). The total claim of "
      f"INR {total:,}, excluding airfare booked by the travel desk, must be submitted on ZEP within "
      f"30 days of return with the hotel invoice attached.")
    scenario_no += 1
leave_scen = [
    ("took 4 consecutive days of casual leave", "Only 3 consecutive days of casual leave are allowed. The fourth day is converted to earned leave, or to LWP if no earned leave balance exists."),
    ("was sick for 3 days and did not submit a certificate", "A medical certificate is required for more than 2 consecutive days. If it is not uploaded within 3 working days of return, the leave is converted to earned leave."),
    ("had 52 days of earned leave on 31 December", "Only 45 days are carried forward; the remaining 7 days lapse."),
    ("joined on 1 July and asked for casual leave", "Casual leave is pro-rated: 6 days for the months July to December."),
    ("wants to combine casual leave with earned leave for a 10-day trip", "Casual leave cannot be combined with earned leave in the same continuous absence; the full trip should be taken as earned leave, applied 7 days in advance."),
    ("became a father and wants paternity leave 4 months after the birth", "Paternity leave must be taken within 3 months of birth or adoption, so the request cannot be approved as paternity leave; earned leave may be used instead."),
    ("resigned with 30 days of earned leave balance", "The 30 days are encashed at the last drawn basic salary as part of the full and final settlement."),
    ("wants to work remotely from Kerala for 3 weeks", "Up to 12 days of full remote work per year can be requested 5 working days in advance; beyond 12 days, leave or a department head exception is required."),
    ("submitted an expense claim 45 days after the expense", "Claims between 31 and 60 days need additional approval from the department head before Finance processes them."),
    ("submitted a taxi claim for INR 350 without a receipt", "Allowed as a self-declared expense, since it is below INR 500, provided monthly self-declared expenses stay within INR 2,000."),
    ("lost a laptop in a cab and reported it the next morning", "Loss must be reported to IT within 2 hours. The delay is recorded, and if negligence is established the employee may bear 25% of the depreciated value."),
    ("received a gift hamper worth INR 5,000 from a vendor", "Gifts above INR 2,000 must be declared to compliance within 5 days and may need to be returned."),
    ("asked to claim a traffic fine incurred while driving to a client", "Traffic fines are never reimbursable."),
    ("wants to buy a monitor for home", "The one-time home office allowance of INR 15,000 in the first year can be used, reimbursed against the bill on ZEP. Alternatively, request a monitor through IT-01 Hardware Request."),
]
for i, (situation, outcome) in enumerate(leave_scen):
    n = names[(i + 5) % len(names)]
    h2(f"G.{scenario_no} {n} {situation}")
    p(f"<b>Situation:</b> {n}, based in the {list(regional)[i % 10]} office, {situation}. "
      f"{n} raised the question with the HR Helpdesk to understand how the policy applies.")
    p(f"<b>Outcome:</b> {outcome}")
    p("<b>Guidance for managers:</b> apply the policy consistently, record the decision on the "
      "portal, and direct the employee to the relevant chapter so they understand the reasoning. "
      "Where the case is unclear, consult the HR Business Partner before responding.")
    scenario_no += 1
for i, (c, a, b) in enumerate(countries[:12]):
    n = names[(i + 3) % len(names)]
    g = grades[(i * 3) % 8]
    days = 3 + i % 5
    rate = a if grades.index(g) <= 4 else b
    h2(f"G.{scenario_no} International trip - {n} ({g}) to {c}")
    p(f"{n}, grade {g}, travelled to {c} for {days} days for a customer delivery review. The "
      f"travel request was raised on ZEP 25 days before departure and approved by the reporting "
      f"manager and the department head (international travel always needs department head approval).")
    p(f"<b>Outcome:</b> the daily allowance for {g} in {c} is USD {rate} per day, so the allowance "
      f"is USD {rate * days} for {days} days, paid in INR at the exchange rate on the date of claim "
      f"approval. Hotel is booked by the travel desk within the cap of USD {a * 2 + 40} per night. "
      f"If breakfast is included, the daily allowance is reduced by 25% for each such day. A forex "
      f"card may be issued against a travel advance of up to 75% of the estimated cost, to be settled "
      f"within 15 days of return.")
    scenario_no += 1
br()

h1("Annexure K - Manager's Quick Guide")
standard_frame(("K", "Manager Responsibilities Guide"), "Head of Human Resources", [
    ("Approvals and Timelines", [("table", [["Request", "Approver", "Target time"],
        ["Leave", "Reporting manager", "2 working days (auto-escalates)"],
        ["Expense claim", "Reporting manager", "5 working days"],
        ["Travel request", "Reporting manager (+ dept head for international)", "3 working days"],
        ["Remote work request", "Reporting manager", "3 working days"],
        ["Attendance regularisation", "Reporting manager", "3 working days"],
        ["Probation recommendation", "Reporting manager", "By end of month 5"]],
        [5 * cm, 6.5 * cm, 5 * cm])]),
    ("One-on-One Meetings", ["Managers are expected to hold a one-on-one meeting with each direct "
                             "report at least <b>once every two weeks</b>, focused on priorities, "
                             "blockers, wellbeing and development."]),
    ("Handling Sensitive Situations", ["Managers must escalate any complaint of harassment to the IC "
                                       "and any suspected fraud to the Ethics Hotline, and must not "
                                       "investigate such matters themselves."]),
    ("Team Budgets", ["Each team has an annual team-engagement budget of INR 2,500 per team member, "
                      "for team lunches and offsites, claimed on ZEP with a list of attendees."]),
])

# ---------------------------------------------------------------- Annexure H office guides
h1("Annexure H - Office Location Guides")
metro = {"Gurugram": "Cyber City Rapid Metro, 8 minutes walk", "Noida": "Noida Sector 62 Metro, 10 minutes walk",
         "Bengaluru": "company shuttle from Marathahalli every 20 minutes", "Pune": "company shuttle from Kharadi bypass",
         "Mumbai": "BKC Metro Line 3 station, 6 minutes walk", "Hyderabad": "HITEC City Metro, 12 minutes walk",
         "Chennai": "company shuttle from Thoraipakkam", "Kolkata": "Sector V Metro, 5 minutes walk",
         "Ahmedabad": "GIFT City internal bus", "Kochi": "Infopark feeder bus from Kakkanad junction"}
for office in regional:
    h2(f"H - {office}")
    p(f"<b>Address:</b> {addresses[office]}. <b>Getting there:</b> {metro[office]}.")
    p(f"<b>Parking:</b> four-wheeler parking is allocated by the Administration team on request "
      f"through form ADM-02; two-wheeler parking is available on a first-come basis. EV charging "
      f"points are available in the basement at no cost to employees.")
    p("<b>Late-night transport:</b> employees leaving after 8:30 PM can book a company cab on the "
      "Admin portal by 5:00 PM the same day. Female employees leaving after 8:30 PM are dropped "
      "first on shared routes and a security guard accompanies cabs after 10:00 PM.")
    table([["Contact", "Details"],
           ["Facilities", f"facilities.{office.lower()}@zenithcorp.example"],
           ["Security desk (24x7)", f"Extension 5{list(regional).index(office)}00"],
           ["First aid / medical room", "Ground floor, open 9:00 AM - 7:00 PM"],
           ["Nearest hospital", f"Empanelled multi-speciality hospital, {office} (details on intranet)"],
           ["Fire assembly point", "Main parking lot, marked with green signage"]],
          [5 * cm, 11.5 * cm])
    p("<b>Emergency procedure:</b> on hearing the fire alarm, leave by the nearest exit using the "
      "stairs (never the lifts), proceed to the assembly point and report to your floor warden. "
      "Evacuation drills are held twice a year. Report any safety hazard to the facilities team.")
    p("<b>Meeting rooms:</b> rooms are booked through the calendar in Zenith Mail. Bookings not "
      "checked in within 10 minutes of the start time are released automatically. Rooms with "
      "video-conferencing equipment are marked VC in the room name.")
    br()

# ---------------------------------------------------------------- Annexure I IT SOPs
h1("Annexure I - IT Standard Operating Procedures")
sops = [
    ("Setting up MFA on a new phone", ["Install the Zenith Authenticator app from the app store.", "On your laptop, open it.zenithcorp.example and choose Security, then Re-register MFA.", "Scan the QR code with the app.", "Enter the 6-digit code to confirm.", "Remove the old device from the list."]),
    ("Connecting to the VPN", ["Open the GlobalConnect client.", "Enter vpn.zenithcorp.example as the portal if prompted.", "Sign in with your Zenith email and password.", "Approve the MFA prompt.", "Wait for the status to show Connected before opening internal applications."]),
    ("Resetting a forgotten password", ["Go to the self-service reset page on the login screen.", "Verify with the Zenith Authenticator app.", "Choose a new password meeting the 12-character rule.", "Sign in again on all devices, including mobile email."]),
    ("Requesting new software", ["Open the Zenith Software Center.", "Search for the application.", "If listed, click Install; no approval needed.", "If not listed, raise form IT-02 with a business justification; approval takes up to 5 working days."]),
    ("Reporting a lost or stolen device", ["Call extension 4357 immediately (within 2 hours).", "IT will remotely lock and wipe the device.", "File a police report within 24 hours.", "Upload the report on form IT-04."]),
    ("Setting up email on your phone", ["Install the approved mail app from the Zenith Software Center mobile catalogue.", "Enrol the phone in device management when prompted.", "Sign in and approve MFA.", "A work profile is created; company data stays separate from personal data."]),
    ("Sharing files with external parties", ["Upload the file to Zenith Drive.", "Choose Share, then External, and enter the recipient's email.", "Set an expiry date (maximum 30 days).", "Confidential files require manager approval; Restricted files may not be shared externally."]),
    ("Joining video meetings from a meeting room", ["Tap the room console to wake it.", "Select the meeting from the room calendar.", "Tap Join; the camera and microphone start automatically.", "Report faulty equipment through the IT portal as a P3 ticket."]),
    ("Backing up your work", ["Save work files in Zenith Drive, which is backed up daily.", "Do not store work files only on the local desktop.", "Deleted files can be recovered within 30 days from the Drive recycle bin."]),
    ("Returning IT assets on exit", ["Log out of all accounts and remove personal files.", "Hand over the laptop, charger and accessories at the IT desk on your last working day.", "Collect the signed asset return receipt, which is required for exit clearance."]),
    ("Printing securely", ["Send the job to the Zenith-SecurePrint queue.", "Walk to any office printer.", "Tap your access badge to release the print job.", "Jobs not released within 24 hours are deleted."]),
    ("Requesting admin rights temporarily", ["Raise an IT-03 access request selecting Temporary Admin.", "Justify the need; manager approval is required.", "Rights are granted for a maximum of 8 hours and all activity is logged."]),
]
for title_s, steps in sops:
    h2(f"I - {title_s}")
    p(f"This procedure explains how to {title_s[0].lower() + title_s[1:]}. If you run into problems "
      f"at any step, raise a ticket on the IT portal or call the IT Service Desk on extension 4357.")
    numbered(steps)
    p("Security reminder: IT staff will never ask for your password or an MFA code. Report any "
      "such request as a security incident to security@zenithcorp.example.")
br()

# ---------------------------------------------------------------- Supplementary policies
h1("Supplementary Policy S1 - Medical Insurance and Claims")
standard_frame(("S1", "Medical Insurance Policy"), "Head of Total Rewards", [
    ("Coverage", ["The group medical policy provides a family floater cover of INR 5,00,000 per "
                  "year. Employees may buy a top-up of INR 5,00,000 or INR 10,00,000 at group rates, "
                  "deducted from salary, during the enrolment window in April.",
                  ["Maternity benefit: up to INR 75,000 for normal delivery and INR 1,00,000 for caesarean.",
                   "Pre-existing diseases covered from day one.", "Room rent capped at 1% of sum insured per day for a normal room and 2% for ICU.",
                   "Pre-hospitalisation 30 days and post-hospitalisation 60 days.",
                   "Parents cover carries a 20% co-payment."]]),
    ("Cashless Claims", [("num", ["Choose a network hospital from the insurer's list on the intranet.",
                                  "Show your e-card at the hospital insurance desk.",
                                  "For planned admission, request pre-authorisation 48 hours in advance.",
                                  "For emergencies, the hospital must inform the insurer within 24 hours of admission."])]),
    ("Reimbursement Claims", ["For treatment at non-network hospitals, submit original bills, discharge "
                              "summary and reports to the insurer's claims portal within <b>30 days</b> of "
                              "discharge. Claims are settled within 30 days of receiving complete documents."]),
    ("Enrolling Dependants", ["New dependants (spouse after marriage, newborn child) must be added "
                              "within <b>30 days</b> of the event through the Zenith People Portal under "
                              "Benefits. Outside this window, dependants can be added only at the April enrolment."]),
])
h1("Supplementary Policy S2 - Relocation")
standard_frame(("S2", "Relocation Policy"), "Head of Human Resources", [
    ("Eligibility", ["Relocation support applies to new joiners asked to relocate by more than 100 km "
                     "and to employees transferred at the company's request."]),
    ("Relocation Benefits", [("table", [["Benefit", "G1 - G4", "G5 - G8"],
                                        ["Travel for employee and family", "Economy air / AC 2-tier", "Economy air"],
                                        ["Temporary accommodation", "7 nights", "15 nights"],
                                        ["Household goods shifting", "Up to INR 40,000", "Up to INR 1,00,000"],
                                        ["Relocation allowance (one-time)", "INR 25,000", "INR 50,000"]],
                              [6 * cm, 5 * cm, 5 * cm])]),
    ("Claw-back", ["If the employee resigns within <b>12 months</b> of relocation, relocation costs "
                   "are recovered on a pro-rata basis from the full and final settlement."]),
])
h1("Supplementary Policy S3 - Learning and Development")
standard_frame(("S3", "Learning and Development Policy"), "Head of Learning", [
    ("Learning Allowance", ["Each employee has a learning allowance of INR 25,000 per financial year "
                            "for courses, certifications and conferences relevant to their role, "
                            "pre-approved by the manager on the Zenith Learning Hub."]),
    ("Study Leave", ["Employees may take up to <b>5 days of paid study leave</b> per year to appear for "
                     "exams of approved certifications."]),
    ("Sponsored Higher Education", ["Employees with 2 or more years of service may apply for "
                                    "sponsorship of up to 50% of fees (maximum INR 3,00,000) for an "
                                    "approved part-time degree. Sponsored employees sign a 24-month "
                                    "service commitment; leaving earlier requires pro-rata repayment."]),
    ("Learning Hours", ["Every employee is expected to complete at least <b>40 learning hours</b> per "
                        "year, tracked on the Zenith Learning Hub."]),
])
h1("Supplementary Policy S4 - Rewards and Recognition")
standard_frame(("S4", "Rewards and Recognition Policy"), "Head of Total Rewards", [
    ("Spot Awards", ["Managers may give Spot Awards of INR 5,000 as e-vouchers for exceptional "
                     "contributions, up to 4 per team member per year."]),
    ("Quarterly Stars", ["Each department nominates up to 2 Quarterly Stars, who receive INR 15,000 "
                         "and a certificate from the CEO."]),
    ("Long Service Awards", [("table", [["Years of service", "Award"], ["5 years", "INR 20,000 voucher"],
                                        ["10 years", "INR 50,000 voucher and 5 extra days of EL"],
                                        ["15 years", "INR 1,00,000 voucher"]], [6 * cm, 10 * cm])]),
    ("Peer Recognition", ["Employees may send Kudos points on the Zenith People Portal; 1,000 Kudos "
                          "points can be redeemed for INR 1,000 in the rewards catalogue."]),
])
h1("Supplementary Policy S5 - Health, Safety and Wellbeing")
standard_frame(("S5", "Health and Safety Policy"), "Head of Administration", [
    ("Workplace Safety", ["Every floor has trained fire wardens and first-aiders, listed on the notice "
                          "board. Any accident or near-miss must be reported to the facilities team "
                          "within 24 hours."]),
    ("Wellbeing Programme", ["Employees receive a wellness allowance of INR 6,000 per year, usable for "
                             "gym memberships, yoga classes or fitness apps, claimed on ZEP."]),
    ("Mental Health", ["The Employee Assistance Programme offers up to 6 free counselling sessions per "
                       "issue for employees and their dependants, available 24x7 on 1800-000-4321. "
                       "All sessions are confidential."]),
])
h1("Supplementary Policy S6 - Data Privacy")
standard_frame(("S6", "Data Privacy Policy"), "Data Protection Officer", [
    ("Principles", ["Zenith Corp processes personal data in line with the Digital Personal Data "
                    "Protection Act, 2023. Personal data is collected only for a specified purpose, "
                    "kept accurate, retained only as long as necessary and protected by appropriate security."]),
    ("Employee Data", ["HR retains employee records for 8 years after separation. Employees can view "
                       "and correct their personal data on the Zenith People Portal and can raise "
                       "privacy requests with dpo@zenithcorp.example."]),
    ("Data Breaches", ["A suspected personal data breach must be reported to security@zenithcorp.example "
                       "within 1 hour. The Data Protection Officer decides on notification to the "
                       "Data Protection Board and affected individuals."]),
])
h1("Supplementary Policy S7 - Prevention of Sexual Harassment (POSH)")
standard_frame(("S7", "POSH Policy"), "Presiding Officer, Internal Committee", [
    ("Internal Committee", ["Each office has an Internal Committee (IC) with a woman Presiding Officer, "
                            "at least two employee members and one external member, as required by "
                            "the POSH Act, 2013."]),
    ("Filing a Complaint", ["A written complaint may be submitted to ic@zenithcorp.example within "
                            "<b>3 months</b> of the incident (extendable by a further 3 months for "
                            "valid reasons). The IC completes its inquiry within <b>90 days</b>."]),
    ("Confidentiality and Non-Retaliation", ["The identity of the complainant, respondent and witnesses "
                                             "is kept confidential. Retaliation against anyone who "
                                             "files a complaint or participates in an inquiry is misconduct."]),
])

h1("Supplementary Policy S8 - Social Media")
standard_frame(("S8", "Social Media Policy"), "Head of Corporate Communications", [
    ("Personal Accounts", ["Employees may mention that they work at Zenith Corp on personal social "
                           "media but must make clear that views are their own. Confidential "
                           "information, customer names and unreleased product details must never be posted."]),
    ("Speaking for the Company", ["Only authorised spokespersons from Corporate Communications may "
                                  "speak on behalf of Zenith Corp. Media enquiries must be forwarded "
                                  "to media@zenithcorp.example within the same working day."]),
])
h1("Supplementary Policy S9 - Company Assets and Facilities")
standard_frame(("S9", "Asset and Facilities Policy"), "Head of Administration", [
    ("Asset Custody", ["Every asset issued to an employee (laptop, phone, access badge, headset) is "
                       "recorded against their name in the asset management tool. Employees are "
                       "responsible for reasonable care of assets in their custody."]),
    ("Access Badges", ["A lost access badge must be reported to the security desk immediately so it "
                       "can be deactivated. A replacement badge costs <b>INR 500</b>, recovered from "
                       "salary, from the second replacement onwards."]),
    ("Desk Booking", ["Offices operate on hot-desking. Desks are booked on the Zenith Workplace app up "
                      "to 14 days in advance. Personal items must be cleared from desks at the end of each day."]),
])

# ---------------------------------------------------------------- Annexure F glossary
h1("Annexure J - Glossary")
glossary = [
    ("CL", "Casual Leave"), ("SL", "Sick Leave"), ("EL", "Earned Leave, also called Privilege Leave"),
    ("LWP", "Leave Without Pay"), ("ZEP", "Zenith Expense Portal, the system for expense claims and travel requests"),
    ("HRBP", "HR Business Partner"), ("IC", "Internal Committee under the POSH Act"),
    ("POSH", "Prevention of Sexual Harassment"), ("PIP", "Performance Improvement Plan"),
    ("MFA", "Multi-factor authentication"), ("VPN", "Virtual Private Network"),
    ("F and F", "Full and final settlement"), ("DA", "Daily allowance or per diem"),
    ("EAP", "Employee Assistance Programme"), ("GST", "Goods and Services Tax"),
]
table([["Term", "Meaning"]] + [[a, b] for a, b in glossary], [3 * cm, 13.5 * cm])


# ---------------------------------------------------------------- page numbers + build
def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawString(2 * cm, 1.2 * cm, "Zenith Corp - Employee Policy Handbook v2.0 - Internal")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    doc = SimpleDocTemplate(OUT_FILE, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm,
                            title="Zenith Corp Employee Policy Handbook", author="Zenith Corp HR")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    from pypdf import PdfReader
    print(f"Created {OUT_FILE} with {len(PdfReader(OUT_FILE).pages)} pages")
