# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Event Organizers:** Local cultural catalysts, indie collective leads, and market coordinators putting together pop-ups across Metro Cebu. They need to secure venues, calculate permits, publish listings, recruit vendors, and hire gig staff.
- **Vendors & Artisans:** Food entrepreneurs, vintage thrifters, printmakers, and craftspeople seeking booth slots with transparent sizing, power requirements, and compliance specs.
- **Performers & Gig Workers:** Indie musicians, DJs, photographers, setup crew, and marshals applying for open event roles.
- **Attendees & Explorers:** Cebu locals and visitors seeking weekend markets, street food bazaars, and creative community gatherings ("Sama ta sa pop-up").

## Product Purpose

Pop-Off Cebu is a hyper-local pop-up engine and discovery hub for Metro Cebu. It lowers the barrier to running grass-roots cultural and commercial pop-ups by demystifying municipal permits and providing a unified coordination space for organizers, booth vendors, performers, and attendees. Success means vibrant, recurring, legally compliant community events with thriving foot traffic and local creator commerce.

## Positioning

Unlike generic ticketing platforms (Eventbrite) or social media groups (Facebook events), Pop-Off Cebu is tailored specifically to Metro Cebu's local geography, culture, and municipal compliance landscape—integrating automatic local permit checklists (Barangay, City Health, CCTO, Fire Safety) with vendor booth tiers and gig recruitment.

## Operating Context

- **Local Geography:** Metro Cebu districts (Cebu City, Mandaue, Lapu-Lapu, Talisay, etc.) and specific barangays that govern municipal jurisdiction.
- **LGU Realities:** Navigating bureaucratic physical filings at City Hall, Barangay Halls, and City Traffic Operations (CCTO).
- **Physical Event Dynamics:** Pop-up booth constraints (booth dimensions in meters, wattage limits for hot cooking vs dry goods), sound checks, and call times.

## Capabilities and Constraints

- **Four Distinct Roles:** `ORGANIZER`, `VENDOR`, `PERFORMER`, and `ATTENDEE` with dedicated role-based views.
- **Automated Permit Triggers:** Generates required municipal permits based on event criteria (food stalls trigger City Health; road closures trigger CCTO; ticketed entry triggers Mayor's Permit; venues trigger Barangay clearance).
- **Booth Tier Management:** Organizers define booth types, dimensions, electrical capacity, and fees; vendors submit applications referencing reusable profiles and compliance documents.
- **Gig Marketplace:** Organizers post short-term roles (entertainment, media, operations); performers and crew submit applications.
- **Discovery & RSVP:** Public schedule (itinerary items), announcements, categorized discovery, and RSVP tracking ("Going", "Interested", "Saved").
- **Technical Architecture:** Django monolithic backend (Django 5.2), Django server-rendered templates, Vanilla CSS, SQLite / PostgreSQL.

## Brand Commitments

- **Tone & Voice:** Vibrant Cebuano-English blend ("Sama ta sa pop-up", "Sama ko!"), community-rooted, practical, and spirited.
- **Visual Identity Root:** Neo-brutalist retro-computing meets Cebu fiesta warmth ("Windows 95 / `.EXE`" cards with warm paper, Utilitarian Green, Rust Accent, and Mustard Pop). Space Grotesk for display typography, IBM Plex Mono for technical and operational labels.

## Evidence on Hand

- Fully scaffolded Django data models covering `accounts`, `events`, `permits`, `vendors`, `gigs`, `profiles`, and `core` districts.
- Established design tokens and base styles in `static/css/base.css` and `static/css/components.css`.
- Seeded template layouts for home discovery, window cards, and role badges.

## Product Principles

- **Rooted in Local Ground Truth:** Design for the actual streets, barangays, and municipal offices of Metro Cebu, not a sanitized Silicon Valley abstraction.
- **Clarity Over Bureaucracy:** Transform intimidating municipal compliance and event logistics into clear, actionable, stress-free checklists.
- **Fair Play for Creators:** Provide equal dignity and clarity to all participants—from solo thrifters and acoustic acts to veteran market organizers.
- **High-Rhythm Discovery:** Keep finding events as joyful, effortless, and fast as stumbling upon a buzzing weekend market.

## Accessibility & Inclusion

- Responsive web accessibility conforming to WCAG 2.1 AA standards.
- High-contrast typography supporting readable text over retro-paper backgrounds.
- Semantic HTML and keyboard-navigable interactive controls.
