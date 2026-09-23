"""Sample data used to populate the database on first run.

This is the demo dataset: 8 students and 16 volunteer opportunities around
Coimbatore, Tamil Nadu, India. Every student has their own mix of skills,
interests, availability, location, and a short bio — so different matching
factors shine for different people. Coordinates and pincodes are real
neighborhoods (Gandhipuram, Peelamedu, Saravanampatti, Vadavalli,
PN Palayam, Singanallur...), good enough for the demo's distance math.
"""
from typing import Any

from . import db

STUDENTS: list[dict[str, Any]] = [
    {
        "name": "Kavya Sridhar",
        "school": "Stanes Anglo Indian Higher Secondary School",
        "grade": "Class 11",
        "zip_code": "641035",
        "latitude": 11.0574,
        "longitude": 77.0187,
        "max_hours_per_week": 6,
        "skills": ["dog-handling", "social-media", "fundraising"],
        "interests": ["animals", "environment", "arts"],
        "bio": "Animal lover hoping to turn her passion into action; "
               "spends weekends at city shelters and curates street-dog "
               "adoption content online.",
    },
    {
        "name": "Arjun Raghavan",
        "school": "Delhi Public School, Coimbatore",
        "grade": "Class 12",
        "zip_code": "641006",
        "latitude": 11.0217,
        "longitude": 76.9868,
        "max_hours_per_week": 8,
        "skills": ["python", "web-dev", "tutoring", "coding", "data-analysis"],
        "interests": ["technology", "education"],
        "bio": "Aspiring software engineer who teaches coding to younger "
               "kids at weekend bootcamps and wants to put his tech skills "
               "to work for nonprofits.",
    },
    {
        "name": "Divya Narayanan",
        "school": "NSN Memorial Global School",
        "grade": "Class 10",
        "zip_code": "641004",
        "latitude": 11.0201,
        "longitude": 77.0116,
        "max_hours_per_week": 5,
        "skills": ["cooking", "tamil", "event-planning", "communication"],
        "interests": ["food", "education", "community"],
        "bio": "Loves cooking family recipes and dreams of running a "
               "community kitchen that feeds everyone in Peelamedu.",
    },
    {
        "name": "Gokul Krishnan",
        "school": "SSVM World School",
        "grade": "Class 9",
        "zip_code": "641041",
        "latitude": 10.9925,
        "longitude": 76.8982,
        "max_hours_per_week": 4,
        "skills": ["photography", "writing", "gardening", "art"],
        "interests": ["environment", "arts", "education"],
        "bio": "Quiet nature photographer who journals about the Western "
               "Ghats and city parks, and wants to help care for green "
               "spaces.",
    },
    {
        "name": "Priya Mohan",
        "school": "SBOA Matriculation & Higher Secondary School",
        "grade": "Class 11",
        "zip_code": "641023",
        "latitude": 10.9691,
        "longitude": 76.9940,
        "max_hours_per_week": 6,
        "skills": ["first-aid", "communication", "organization", "nursing"],
        "interests": ["health", "elderly-care"],
        "bio": "Pre-med hopeful who volunteers at an old age home and wants "
               "hands-on caregiving experience.",
    },
    {
        "name": "Surya Subramanian",
        "school": "Vidya Vikasini Matriculation Higher Secondary School",
        "grade": "Class 12",
        "zip_code": "641037",
        "latitude": 11.0645,
        "longitude": 76.9080,
        "max_hours_per_week": 7,
        "skills": ["graphic-design", "event-planning", "public-speaking", "social-media"],
        "interests": ["arts", "community", "technology"],
        "bio": "Designer and occasional MC at college fests and local "
               "kacheris, who wants to make community events beautiful and "
               "well-attended.",
    },
    {
        "name": "Nithya Raman",
        "school": "Kovai Public School",
        "grade": "Class 12",
        "zip_code": "641005",
        "latitude": 11.0058,
        "longitude": 77.0145,
        "max_hours_per_week": 5,
        "skills": ["data-analysis", "web-dev", "tamil", "communication", "website"],
        "interests": ["technology", "community", "education"],
        "bio": "Bilingual (Tamil and English) aspiring product manager who "
               "rebuilt two local nonprofits' websites and wants to keep "
               "giving back to the community.",
    },
    {
        "name": "Rahul Venkat",
        "school": "Hindusthan Matriculation Higher Secondary School",
        "grade": "Class 10",
        "zip_code": "641034",
        "latitude": 11.0825,
        "longitude": 76.9580,
        "max_hours_per_week": 6,
        "skills": ["tutoring", "first-aid", "english", "math"],
        "interests": ["animals", "health", "education"],
        "bio": "Patient maths tutor who loves shelter dogs and wants to "
               "combine teaching with caregiving.",
    },
]

OPPORTUNITIES: list[dict[str, Any]] = [
    {
        "title": "Weekend Reading Buddies",
        "org_name": "Coimbatore District Central Library",
        "category": "education",
        "description": "Read one-on-one with primary-school kids to build "
                       "confidence and early literacy skills in a lively "
                       "library setting.",
        "tags": ["tutoring", "kids", "literacy"],
        "zip_code": "641012",
        "latitude": 11.0168,
        "longitude": 76.9558,
        "hours_min": 3,
        "hours_max": 5,
        "required_skills": ["tutoring"],
        "helpful_skills": ["english", "public-speaking"],
    },
    {
        "title": "Tech Tutoring for Seniors",
        "org_name": "Coimbatore Senior Citizens' Association",
        "category": "elderly-care",
        "description": "Teach grocery apps, video calls, and email basics to "
                       "older adults who want to stay connected with family.",
        "tags": ["tutoring", "elderly", "technology"],
        "zip_code": "641002",
        "latitude": 10.9989,
        "longitude": 76.9654,
        "hours_min": 2,
        "hours_max": 4,
        "required_skills": ["tutoring"],
        "helpful_skills": ["communication", "tamil", "computer-basics"],
    },
    {
        "title": "Noyyal River Cleanup Crew",
        "org_name": "Siruthuli",
        "category": "environment",
        "description": "Help pull trash from the Noyyal riverbank, bag "
                       "plastic waste, and catalog native trees planted "
                       "along the restoration stretch.",
        "tags": ["environment", "outdoors", "river"],
        "zip_code": "641001",
        "latitude": 10.9926,
        "longitude": 76.9570,
        "hours_min": 2,
        "hours_max": 3,
        "required_skills": [],
        "helpful_skills": ["gardening", "photography", "organization"],
    },
    {
        "title": "Adoption Day Crew",
        "org_name": "ARRC — Animal Rescue and Rehabilitation Centre",
        "category": "animal-welfare",
        "description": "Handle adoptable street dogs during weekend adoption "
                       "camps, talk with prospective families, and manage "
                       "the paperwork table.",
        "tags": ["animals", "events", "dogs"],
        "zip_code": "641037",
        "latitude": 11.0645,
        "longitude": 76.9080,
        "hours_min": 4,
        "hours_max": 6,
        "required_skills": ["dog-handling"],
        "helpful_skills": ["social-media", "fundraising", "communication"],
    },
    {
        "title": "Community Kitchen Crew",
        "org_name": "No Food Waste Foundation — Coimbatore",
        "category": "food-and-hunger",
        "description": "Help sort surplus food, prep and pack meals in the "
                       "community kitchen for distribution to the needy.",
        "tags": ["food", "cooking", "community"],
        "zip_code": "641004",
        "latitude": 11.0201,
        "longitude": 77.0116,
        "hours_min": 3,
        "hours_max": 5,
        "required_skills": ["cooking"],
        "helpful_skills": ["tamil", "event-planning", "organization"],
    },
    {
        "title": "Robotics Competition Judges",
        "org_name": "CodeiGma — Avishkar Robotics",
        "category": "education",
        "description": "Judge student robotics teams at a high-energy "
                       "competition, scoring engineering notebooks and "
                       "interviewing teams on their build process.",
        "tags": ["technology", "robotics", "competition"],
        "zip_code": "641035",
        "latitude": 11.0574,
        "longitude": 77.0187,
        "hours_min": 4,
        "hours_max": 8,
        "required_skills": ["coding"],
        "helpful_skills": ["python", "tutoring", "data-analysis"],
    },
    {
        "title": "Art Therapy Workshop Assistant",
        "org_name": "Kovai Art Therapy Trust",
        "category": "health",
        "description": "Help set up art supplies and support participants in "
                       "guided art therapy workshops for adults managing "
                       "mental health challenges.",
        "tags": ["arts", "mental-health", "therapy"],
        "zip_code": "641041",
        "latitude": 10.9925,
        "longitude": 76.8982,
        "hours_min": 2,
        "hours_max": 4,
        "required_skills": ["art"],
        "helpful_skills": ["photography", "communication"],
    },
    {
        "title": "Organic Farm Volunteers",
        "org_name": "OSAI — Society for Sustainable Agriculture",
        "category": "environment",
        "description": "Plant, weed, water, and harvest at an organic farm "
                       "in the city suburbs that grows produce for local "
                       "families and teaches natural farming.",
        "tags": ["gardening", "outdoors", "sustainability"],
        "zip_code": "641042",
        "latitude": 11.0180,
        "longitude": 76.9971,
        "hours_min": 3,
        "hours_max": 6,
        "required_skills": ["gardening"],
        "helpful_skills": ["photography", "organization", "teamwork"],
    },
    {
        "title": "Spoken English Practice Circles",
        "org_name": "Nanban Trust",
        "category": "education",
        "description": "Lead relaxed spoken-English conversation groups for "
                       "first-generation learners of all ages to practice "
                       "everyday language and build confidence.",
        "tags": ["tutoring", "literacy", "spoken-english"],
        "zip_code": "641023",
        "latitude": 10.9691,
        "longitude": 76.9940,
        "hours_min": 2,
        "hours_max": 3,
        "required_skills": ["english"],
        "helpful_skills": ["tamil", "communication", "tutoring"],
    },
    {
        "title": "Senior Companionship Program",
        "org_name": "Little Flower Home for the Aged",
        "category": "elderly-care",
        "description": "Visit residents for conversation, board games, and "
                       "walks, building lasting one-on-one friendships.",
        "tags": ["elderly", "companionship", "home-visits"],
        "zip_code": "641005",
        "latitude": 11.0058,
        "longitude": 77.0145,
        "hours_min": 2,
        "hours_max": 4,
        "required_skills": ["communication"],
        "helpful_skills": ["first-aid", "organization"],
    },
    {
        "title": "First Aid for Youth Sports",
        "org_name": "Coimbatore District Sports Association",
        "category": "health",
        "description": "Provide first-aid coverage at community youth "
                       "cricket, football, and kabaddi matches on weekend "
                       "mornings.",
        "tags": ["sports", "youth", "safety"],
        "zip_code": "641402",
        "latitude": 11.0333,
        "longitude": 77.1272,
        "hours_min": 2,
        "hours_max": 3,
        "required_skills": ["first-aid"],
        "helpful_skills": ["communication", "teamwork"],
    },
    {
        "title": "Blood Donation Camp Coordinators",
        "org_name": "Indian Red Cross — Coimbatore District Blood Bank",
        "category": "health",
        "description": "Check donors in, run the refreshment table, and help "
                       "people through the donation flow at monthly blood "
                       "donation camps.",
        "tags": ["health", "events", "drives"],
        "zip_code": "641006",
        "latitude": 11.0217,
        "longitude": 76.9868,
        "hours_min": 3,
        "hours_max": 5,
        "required_skills": ["organization"],
        "helpful_skills": ["event-planning", "communication", "first-aid"],
    },
    {
        "title": "Museum Guide and Usher",
        "org_name": "G.D. Naidu Charities — Science & Industrial Museum",
        "category": "arts-culture",
        "description": "Greet visitors, run hands-on science discovery carts, "
                       "and give short guided tours about the museum's "
                       "history to school groups.",
        "tags": ["arts", "history", "museums"],
        "zip_code": "641004",
        "latitude": 11.0201,
        "longitude": 77.0116,
        "hours_min": 4,
        "hours_max": 6,
        "required_skills": ["public-speaking"],
        "helpful_skills": ["communication", "art", "writing"],
    },
    {
        "title": "Nonprofit Website Refresh",
        "org_name": "COSS — Coimbatore Open Source Society",
        "category": "technology",
        "description": "Redesign and re-platform outdated nonprofit websites, "
                       "improve accessibility, and document the codebase so "
                       "orgs can maintain it themselves.",
        "tags": ["technology", "nonprofits", "design"],
        "zip_code": "641035",
        "latitude": 11.0574,
        "longitude": 77.0187,
        "hours_min": 4,
        "hours_max": 6,
        "required_skills": ["web-dev"],
        "helpful_skills": ["python", "data-analysis", "graphic-design", "website"],
    },
    {
        "title": "Street Dog Adoption Social Media Squad",
        "org_name": "VOICE Trust — Animal Welfare",
        "category": "animal-welfare",
        "description": "Photograph rescued street dogs, write adoption "
                       "blurbs, and run the organisation's Instagram to push "
                       "up adoption rates.",
        "tags": ["animals", "pets", "social-media"],
        "zip_code": "641045",
        "latitude": 10.9873,
        "longitude": 76.9908,
        "hours_min": 2,
        "hours_max": 5,
        "required_skills": ["social-media"],
        "helpful_skills": ["photography", "fundraising", "writing"],
    },
    {
        "title": "Home Meal Delivery",
        "org_name": "Akshaya Patra Foundation — Coimbatore",
        "category": "food-and-hunger",
        "description": "Package and deliver hot midday meals to the elderly "
                       "and homebound with a friendly smile.",
        "tags": ["food", "elderly", "delivery"],
        "zip_code": "641011",
        "latitude": 11.0195,
        "longitude": 76.9727,
        "hours_min": 2,
        "hours_max": 4,
        "required_skills": [],
        "helpful_skills": ["communication", "organization", "first-aid"],
    },
]


def seed_if_empty(conn) -> bool:
    """Insert sample data only if the database has no rows yet."""
    if db.count_rows(conn, "students") > 0 or db.count_rows(conn, "opportunities") > 0:
        return False
    for s in STUDENTS:
        db.insert_student(conn, s)
    for o in OPPORTUNITIES:
        db.insert_opportunity(conn, o)
    conn.commit()
    return True