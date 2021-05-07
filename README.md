# ui-health

# How to Run Application:
Requirements:
    - Python 3
1. Run the following command in your shell from project directory:
    ```Shell
    > pip install -r requirements.txt
    > python3 main.py
    ```
3. Open http://127.0.0.1:5000/ in a browser
3. Sign up with 'admin' as email. Password at default will be 'password' to log in as Admin (generating test data will automatically create an Admin account)

# Generate Test Data
Using Flask and the Faker Python library, you can generate test data.

Run command from project directory:
```Shell
> set FLASK_APP=main.py
> flask create-full-profile-database
```

# Project Description
UI-Health allows University of Illinois hospital(UIH) to maintain nurse schedules, Covid-19 vaccination appointments, vaccine availability, and patients to sign up for appointments.

## Functionalities 
### Admin:
1. Register a nurse: nurses cannot self-register. The admin should register them. In addition to the information above, every nurse is assigned a username and a passoword.
2. Update nurse info: any update in nurse info (other than phone # and address) should be carried out by the admin.
3. Delete a nurse: remove a nurse from database.
4. Add Vaccine: upon receiving new doses of a vaccine, the admin updates the repository.
5. Update Vaccine: in any case some vaccine (not on-hold) are removed from the repository, admin updates the number of vaccines.
6. View Nurse info: view the information of a nurse and the times they have scheduled for.
7. View Patient info: view the information of a patient, the times they have scheduled for vaccination, and their vaccination history.

### Nurse:
1. Update information: Nurses can update their address and phone#
2. Schedule time: nurses can schedule for time slots that have less than 12 nurses scheduled for them.
3. Cancel a time: nurses should be able to delete a time they have scheduled for.
4. View Information: Nurses can view their information, including the times they have scheduled for.
5. Vaccination: upon delivering a vaccine, nurses should record the vaccination

### Patient:
1. Register: Patients can register their information. In addition to what described above, a patient needs to pick a username and a password.
2. Update Info: patients can update their information.
3. Schedule a vaccination time: Patients should see the available time slot and be able to select one as their schedule.
4. Cancel Schedule: Patients can delete their scheduled time (which will also release one on-hold vaccine).
5. View information: Patients can see their information, the times they have scheduled for vaccination, and their vaccination history.

# Models
- Vaccine: The core to the vaccination process is vaccine that has a name, name of the company, number of doses required for immunization (e.g., Pfizer requires two doses), and an optional textual description.
- Nurse: The vaccination is carried out by nurses. Every nurse has a name (Fname, MI, Lname), EmployeeID, age, gender, phone#, and address.The vaccination is done during the 1-hr time slots (M, Feb. 15 2021, 10:00-11:00 am). UIH has a mximum capacity (100) on the number of patients it can accept for vaccination at a time slot. UIH needs to have at least one nurse per time slot. Every nurse can vaccinate at most 10 patients during each time slot. As a result, the maximum number of patients that can be vaccinated at time-slot j is:  min⁡(10 ∗ 𝑁𝑗, 100)
- Patient: Every patient has name (Fname, MI, Lname), SSN, age, gender, race, occupation class (e.g. educator, healthcare worker, etc.), medical history description (for simplification, suppose it is plain text), phone#, address.
- Vaccination Record: Every vaccination for a patient is done by a nurse at a specific time. The vaccination record also includes the which vaccine has been used and the dose of vaccine (e.g. PatientX received dose 1 of Pfizer, by NurseY at time-slot j). Upon Vaccination, one vaccine that has been on-hold gets reduced from the repository.
- Nurse Schedule: Information about start and end time of a nurse's schedule

# Sources/Styling
- Bootstrap: https://getbootstrap.com/docs/5.0/getting-started/introduction/
- Login page: https://bootsnipp.com/snippets/92gmX
- Logo styling: https://editor.freelogodesign.org/en/logo/edit/dcfc1bd3c2e54f188a8dd839b9bf33f9?template=3693663
- 403 error page - https://codepen.io/Chesswithsean/pen/ZMwagQ
- Nurses Schedules Page - https://codepen.io/oltika/pen/GNvdgV
- Navbar account dropdown - https://github.com/puikinsh/CoolAdmin
- Patient calendar - https://fullcalendar.io/demos

