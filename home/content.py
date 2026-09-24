"""Page-specific service copy shared by service listings and detail pages."""

# How to reach NEXCODE, shown on the contact page and in reply emails.
CONTACT_DETAILS = {
    "address": "1 KN 78 St, Kigali · Norrsken House Kigali",
    "email": "nexcoderwa@gmail.com",
    "second_email": "",
    "phone_number": "+250 781 862 349",
    "phone_href": "tel:+250781862349",
    "twitter": "https://x.com/nexcodeafrica",
    "linkedin": "https://www.linkedin.com/company/nexcode-rwanda/",
    "instagram": "https://www.instagram.com/nexcode.africa/",
}

SERVICES = {
    "softwareDev": {
        "slug": "software-development",
        "title": "Custom software development",
        "meta_title": "Custom Software Development in Kigali",
        "description": "Custom web applications, business systems and integrations from "
        "NEXCODE in Kigali. Plan, build and maintain software around the "
        "way your team works.",
        "intro": "Replace disconnected tools and manual handoffs with software built "
        "around your operations. We develop websites, web applications and "
        "business systems for teams with a specific problem to solve.",
        "image": "img/services/1.jpg",
        "image_alt": "Hotel booking interface with room details, availability and a map",
        "focus": "Start with the workflow that matters most",
        "body": "A useful first release solves a clear task: accepting a booking, "
        "recording a payment, managing a team or sharing reliable information. We "
        "work with you to define the users, permissions and data behind that task "
        "before adding more features.",
        "deliverables": [
            (
                "Business applications",
                "Bring records, approvals and reporting into one place, with "
                "access tailored to each role.",
            ),
            (
                "Websites and customer portals",
                "Make it easier for customers to find information, submit "
                "requests and follow progress.",
            ),
            (
                "Integrations and smart-card systems",
                "Connect existing services or physical check-ins to the "
                "software your team uses.",
            ),
        ],
        "steps": [
            (
                "Define the first release",
                "Map the current process and agree on the essential features and "
                "acceptance criteria.",
            ),
            (
                "Build and review",
                "Review working increments together so decisions are tested before the "
                "scope grows.",
            ),
            (
                "Launch and maintain",
                "Prepare deployment, documentation and a support plan matched to the "
                "system.",
            ),
        ],
        "scope": "Tell us what your team does today, where work gets delayed, and which "
        "tools the new system needs to connect to. We will use that context to "
        "discuss scope, timing and cost.",
    },
    "uiUx": {
        "slug": "ui-ux",
        "title": "UI/UX design",
        "meta_title": "UI/UX Design for Websites and Apps",
        "description": "Design clearer websites and apps with NEXCODE. Explore user journeys, "
        "interactive prototypes and practical interface design for your next "
        "digital product.",
        "intro": "Help people find what they need and complete tasks with confidence. We turn "
        "product requirements into clear journeys, testable prototypes and interfaces "
        "ready for development.",
        "image": "img/services/ui1.jpg",
        "image_alt": "Illustration of a group reviewing mobile interface prototypes",
        "focus": "Resolve uncertainty before development",
        "body": "A prototype makes a product idea concrete. It lets your team examine "
        "navigation, content and key decisions before investing in a full build. For "
        "existing products, we focus on the steps where people get confused or abandon a "
        "task.",
        "deliverables": [
            (
                "User journeys",
                "Map the path from a user’s starting point to a completed task, "
                "including errors and empty states.",
            ),
            (
                "Interactive prototypes",
                "Explore screen structure and interactions with a prototype your team "
                "can review.",
            ),
            (
                "Interface specifications",
                "Define reusable components, responsive layouts and states that "
                "developers can implement consistently.",
            ),
        ],
        "steps": [
            (
                "Understand the audience",
                "Discuss the product, user needs and available research.",
            ),
            (
                "Explore and validate",
                "Compare flows and review a prototype against real tasks.",
            ),
            (
                "Prepare the handoff",
                "Deliver agreed design files and document behavior, content and accessibility "
                "considerations.",
            ),
        ],
        "scope": "Share your product idea or existing screens, the audience you serve, and the "
        "task you want to improve. We can then identify the most useful design work.",
    },
    "mobileDev": {
        "slug": "mobile-development",
        "title": "Mobile app development",
        "meta_title": "Mobile App Development in Rwanda",
        "description": "Build an Android or iOS app with NEXCODE in Kigali. Plan mobile "
        "workflows, connect business systems and prepare your app for "
        "testing and release.",
        "intro": "Put the tasks your customers or field teams need into an app they can use "
        "on the move. We plan and build mobile products around real devices, "
        "working conditions and business needs.",
        "image": "img/services/md1.jpg",
        "image_alt": "Illustration of a group working on mobile applications",
        "focus": "Choose the platform around your users",
        "body": "An app for a field team has different needs from a customer booking app. "
        "We discuss device availability, connectivity, notifications and account "
        "access before choosing a platform and an approach to development.",
        "deliverables": [
            (
                "Customer applications",
                "Support bookings, requests and account activity through a "
                "focused mobile experience.",
            ),
            (
                "Tools for teams",
                "Design practical workflows for staff who work away from a desk.",
            ),
            (
                "Connected services",
                "Link the app to the accounts, data and business systems it " "needs.",
            ),
        ],
        "steps": [
            (
                "Plan mobile requirements",
                "Agree on platforms, essential journeys and any offline requirements.",
            ),
            (
                "Build and test on devices",
                "Review working screens and test the agreed device and network "
                "conditions.",
            ),
            (
                "Prepare release and support",
                "Handle release preparation and agree on updates; store approval remains "
                "subject to platform review.",
            ),
        ],
        "scope": "Let us know who will use the app, which devices they have, and the core "
        "task it should support. Include any existing backend or app that we need "
        "to work with.",
    },
    "networking": {
        "slug": "networking",
        "title": "Business networking services",
        "meta_title": "Business Networking Services in Kigali",
        "description": "Plan and improve your business network with NEXCODE. Discuss Wi-Fi "
        "coverage, device access and connectivity requirements for your "
        "workplace in Kigali.",
        "intro": "Give your team a dependable connection to the tools they use every day. "
        "We help businesses plan network infrastructure and address workplace "
        "connectivity problems.",
        "image": "img/services/networking1.jpg",
        "image_alt": "Illustration of technicians installing network equipment",
        "focus": "Understand the site before choosing equipment",
        "body": "Coverage, building layout, device numbers and the applications you use "
        "all affect network design. We start with those constraints so the "
        "proposed setup reflects how your workplace operates.",
        "deliverables": [
            (
                "Network planning",
                "Map equipment, cabling and capacity requirements for your "
                "premises.",
            ),
            (
                "Wi-Fi and device access",
                "Plan coverage and separate access for staff, guests and "
                "connected devices where required.",
            ),
            (
                "Troubleshooting and handover",
                "Investigate connection issues and document the agreed "
                "configuration for ongoing support.",
            ),
        ],
        "steps": [
            (
                "Assess the environment",
                "Review the location, current equipment and recurring connectivity "
                "issues.",
            ),
            (
                "Agree on the setup",
                "Define the proposed changes, equipment needs and installation scope.",
            ),
            (
                "Check and document",
                "Test the agreed coverage and connections, then record the setup.",
            ),
        ],
        "scope": "Include your location, approximate number of users and devices, and the "
        "connection problems you want to solve. Site work and equipment are "
        "scoped individually.",
    },
    "digitalMarketing": {
        "slug": "digital-marketing",
        "title": "Digital marketing",
        "meta_title": "Digital Marketing and SEO in Rwanda",
        "description": "Clarify your online message with NEXCODE. Plan website "
        "content, technical SEO and digital campaigns around the "
        "audience and enquiries that matter to your business.",
        "intro": "Help the right people understand your business and take the next "
        "step. We connect website content, search visibility and campaign "
        "planning to a clear business objective.",
        "image": "img/services/dm1.jpg",
        "image_alt": "Illustration of a group reviewing marketing charts",
        "focus": "Measure useful actions, not just attention",
        "body": "A visit matters when it brings someone closer to a useful action: "
        "an enquiry, a booking or a purchase. We agree on the audience and "
        "the desired action first, then identify the content and channels "
        "that can support it.",
        "deliverables": [
            (
                "Website content and SEO",
                "Improve page structure, messages and technical "
                "discoverability around relevant customer questions.",
            ),
            (
                "Social content planning",
                "Build a focused publishing plan with a consistent voice "
                "and a clear purpose for each post.",
            ),
            (
                "Campaign measurement",
                "Define conversion events and review results against the "
                "agreed objective and budget.",
            ),
        ],
        "steps": [
            (
                "Review the starting point",
                "Assess the website, audience and any available campaign data.",
            ),
            (
                "Set priorities",
                "Choose the pages, messages and channels that deserve attention "
                "first.",
            ),
            (
                "Publish and learn",
                "Review results and adjust the plan using evidence rather than "
                "promises of rankings.",
            ),
        ],
        "scope": "Share your website, target audience and business goal. Campaign "
        "fees, advertising spend and reporting needs are agreed separately "
        "before work begins.",
    },
    "maintenance": {
        "slug": "maintenance",
        "title": "Software maintenance and support",
        "meta_title": "Software Maintenance and Support",
        "description": "Keep your website or application supported with NEXCODE. Discuss "
        "bug fixes, updates, performance reviews and a maintenance plan "
        "suited to your system.",
        "intro": "Keep an existing website or application useful as your business "
        "changes. We help investigate issues, plan updates and maintain the "
        "software your operations depend on.",
        "image": "img/services/maintenance1.jpg",
        "image_alt": "Illustration of technicians maintaining network systems",
        "focus": "Make support expectations clear",
        "body": "Support starts with understanding the system and its dependencies. We "
        "agree on access, priorities, response arrangements and what is included, "
        "so routine maintenance and larger feature requests can be planned "
        "appropriately.",
        "deliverables": [
            (
                "Issue investigation",
                "Reproduce reported problems, identify their cause and verify "
                "fixes.",
            ),
            (
                "Planned updates",
                "Review dependency and platform changes, then test updates "
                "before release.",
            ),
            (
                "Performance and reliability reviews",
                "Investigate slow workflows and review backup and recovery "
                "arrangements within the agreed scope.",
            ),
        ],
        "steps": [
            (
                "Review the system",
                "Understand the technology, hosting and known issues.",
            ),
            (
                "Agree on priorities",
                "Set a maintenance scope, communication process and support schedule.",
            ),
            (
                "Maintain and report",
                "Document changes, verify key workflows and flag work that needs "
                "separate planning.",
            ),
        ],
        "scope": "Tell us how the system is hosted, the technologies it uses and any "
        "current issues. Coverage hours and response commitments are defined in "
        "your support agreement.",
    },
}
