curl -s "https://serpapi.com/search?engine=google_local&q=Gym+London+UK&google_domain=google.com&hl=en&gl=uk&device=desktop&api_key=4373c085f2ae35a78b2cc35a236abb78c3be3ff68c39c5beb987ee0f213a92da" | jq

```json
{
  "search_metadata": {
    "id": "68a22c2d079a2bb5f2b6489f",
    "status": "Success",
    "json_endpoint": "https://serpapi.com/searches/12e4e3eb5ff42deb/68a22c2d079a2bb5f2b6489f.json",
    "created_at": "2025-08-17 19:23:25 UTC",
    "processed_at": "2025-08-17 19:23:25 UTC",
    "google_local_url": "https://www.google.com/search?q=Gym+London+UK&hl=en&gl=uk&tbm=lcl",
    "raw_html_file": "https://serpapi.com/searches/12e4e3eb5ff42deb/68a22c2d079a2bb5f2b6489f.html",
    "total_time_taken": 1.2
  },
  "search_parameters": {
    "engine": "google_local",
    "q": "Gym London UK",
    "google_domain": "google.com",
    "hl": "en",
    "gl": "uk",
    "device": "desktop"
  },
  "local_results": [
    {
      "position": 1,
      "rating": 4.8,
      "reviews": 1400,
      "reviews_original": "(1.4K)",
      "description": "\"The gym's atmosphere is motivating, and the modern equipment is excellent.\"",
      "lsig": "AB86z5VXacF7-WDpoOUUGSY6ij-u",
      "links": {
        "website": "https://www.thirdspace.london/clubs/soho/",
        "directions": "https://www.google.com/maps/dir//Third+Space+Soho,+67+Brewer+St,+London+W1F+9US/data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x487604d40da61abd:0x4f349752569e6abd?sa=X&ved=2ahUKEwjn7Y31yJKPAxUsFFkFHb4OLEAQ48ADegQIBBAA&hl=en&gl=uk"
      },
      "place_id": "5707353007681596093",
      "place_id_search": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&ludocid=5707353007681596093&q=Gym+London+UK",
      "gps_coordinates": {
        "latitude": 51.51127,
        "longitude": -0.1357459
      },
      "title": "Third Space Soho",
      "type": "Gym",
      "years_in_business": "10+ years in business",
      "address": "67 Brewer St",
      "phone": "020 7439 6333",
      "hours": "Closed ⋅ Opens 6 am Mon"
    },
    {
      "position": 2,
      "rating": 4.9,
      "reviews": 320,
      "reviews_original": "(320)",
      "description": "\"Gym very well equipped, friendly staff and the best playlist ever!\"",
      "lsig": "AB86z5WGY-B6qEzKLOykT96ujL8a",
      "links": {
        "website": "https://www.anytimefitness.co.uk/gyms/uk-0433/london-fields-hackney-greater-london-e9-7qw/",
        "directions": "https://www.google.com/maps/dir//Anytime+Fitness,+8+Pemberton+Pl,+London+E8+3RG/data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x48761d99ccaaf6f7:0x4eada6b64071ea4b?sa=X&ved=2ahUKEwjn7Y31yJKPAxUsFFkFHb4OLEAQ48ADegQIFRAA&hl=en&gl=uk"
      },
      "place_id": "5669370807624788555",
      "place_id_search": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&ludocid=5669370807624788555&q=Gym+London+UK",
      "gps_coordinates": {
        "latitude": 51.540432,
        "longitude": -0.0549544
      },
      "title": "Anytime Fitness",
      "type": "Gym",
      "years_in_business": "3+ years in business",
      "address": "8 Pemberton Pl",
      "phone": "020 3903 9522",
      "hours": "Open 24 hours"
    },
    {
      "position": 3,
      "rating": 4.8,
      "reviews": 678,
      "reviews_original": "(678)",
      "description": "\"So much equipment, amazing and friendly staff 10/10 gym !\"",
      "lsig": "AB86z5XZsKE6n5PKLmlYlb4J_gPr",
      "links": {
        "website": "https://muscleworksgym.co.uk/",
        "directions": "https://www.google.com/maps/dir//Muscleworks+Gym,+114+Vallance+Rd,+London+E1+5BL/data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x48761cc5ecbf2cb5:0xd6fa9da0f50d0fcb?sa=X&ved=2ahUKEwjn7Y31yJKPAxUsFFkFHb4OLEAQ48ADegQIChAA&hl=en&gl=uk"
      },
      "place_id": "15490867182925844427",
      "place_id_search": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&ludocid=15490867182925844427&q=Gym+London+UK",
      "gps_coordinates": {
        "latitude": 51.52243,
        "longitude": -0.0640227
      },
      "title": "Muscleworks Gym",
      "type": "Gym",
      "years_in_business": "20+ years in business",
      "address": "114 Vallance Rd",
      "phone": "020 7247 0434",
      "hours": "Open 24 hours"
    },
    {
      "position": 4,
      "rating": 5.0,
      "reviews": 836,
      "reviews_original": "(836)",
      "description": "\"Excellent gym, fully staffed and equipment is largely new and laid out well.\"",
      "lsig": "AB86z5WS2EBoIcGmMqzhV2HO3o1e",
      "links": {
        "website": "http://www.gym-nation.co.uk/",
        "directions": "https://www.google.com/maps/dir//Gym+Nation+%7C+London+Bridge,+26+Druid+St,+London+SE1+2EY/data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x4876039c80dde83d:0xb260ae9d8c72d7b?sa=X&ved=2ahUKEwjn7Y31yJKPAxUsFFkFHb4OLEAQ48ADegQIExAA&hl=en&gl=uk"
      },
      "place_id": "803341583012801915",
      "place_id_search": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&ludocid=803341583012801915&q=Gym+London+UK",
      "gps_coordinates": {
        "latitude": 51.50148,
        "longitude": -0.0788046
      },
      "title": "Gym Nation | London Bridge",
      "type": "Gym",
      "address": "26 Druid St",
      "phone": "020 8117 7455",
      "hours": "Closed ⋅ Opens 6 am Mon"
    },
    {
      "position": 5,
      "rating": 4.9,
      "reviews": 608,
      "reviews_original": "(608)",
      "description": "\"The facilities were immaculate and the gym was quiet and well laid out!\"",
      "lsig": "AB86z5VLaYaiU5YaJIGEeoN9Zg90",
      "links": {
        "website": "https://www.thirdspace.london/clubs/mayfair/",
        "directions": "https://www.google.com/maps/dir//Third+Space+Mayfair,+22+Clarges+St,+London+W1J+5FA/data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x4876051f8b713729:0xfb0b591762b817dc?sa=X&ved=2ahUKEwjn7Y31yJKPAxUsFFkFHb4OLEAQ48ADegQIEhAA&hl=en&gl=uk"
      },
      "place_id": "18089650285239080924",
      "place_id_search": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&ludocid=18089650285239080924&q=Gym+London+UK",
      "gps_coordinates": {
        "latitude": 51.50758,
        "longitude": -0.145922
      },
      "title": "Third Space Mayfair",
      "type": "Gym",
      "years_in_business": "3+ years in business",
      "address": "22 Clarges St",
      "phone": "020 7042 6440",
      "hours": "Closed ⋅ Opens 6 am Mon"
    },
    {
      "position": 6,
      "rating": 4.8,
      "reviews": 960,
      "reviews_original": "(960)",
      "description": "\"High quality equipment, friendly staff and great a great vibe to workout in.\"",
      "lsig": "AB86z5XipLPosMdDRWaL2c1bWd-U",
      "links": {
        "website": "https://www.thirdspace.london/clubs/city/",
        "directions": "https://www.google.com/maps/dir//Third+Space+City,+40+Mark+Ln,+London+EC3R+7AT/data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x487604d442622727:0x54383a402c73e234?sa=X&ved=2ahUKEwjn7Y31yJKPAxUsFFkFHb4OLEAQ48ADegQIDxAA&hl=en&gl=uk"
      },
      "place_id": "6068664545179853364",
      "place_id_search": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&ludocid=6068664545179853364&q=Gym+London+UK",
      "gps_coordinates": {
        "latitude": 51.510258,
        "longitude": -0.0805433
      },
      "title": "Third Space City",
      "type": "Gym",
      "years_in_business": "7+ years in business",
      "address": "40 Mark Ln",
      "phone": "020 7534 2888",
      "hours": "Closed ⋅ Opens 6 am Mon"
    },
    {
      "position": 7,
      "rating": 4.8,
      "reviews": 326,
      "reviews_original": "(326)",
      "description": "\"Beautiful gym studio, great professional staff, and a good clientele crowd.\"",
      "lsig": "AB86z5X6WbxKq0HCp3-ntGF-8-d2",
      "links": {
        "website": "https://www.topnotchgyms.co.uk/",
        "directions": "https://www.google.com/maps/dir//Topnotch+Gyms+Soho,+Dufour's+Pl,+London+W1F+7SP/data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x4876058eb8f540cf:0x60d9f454658e00d6?sa=X&ved=2ahUKEwjn7Y31yJKPAxUsFFkFHb4OLEAQ48ADegQIDhAA&hl=en&gl=uk"
      },
      "place_id": "6978877740905529558",
      "place_id_search": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&ludocid=6978877740905529558&q=Gym+London+UK",
      "gps_coordinates": {
        "latitude": 51.513626,
        "longitude": -0.1375165
      },
      "title": "Topnotch Gyms Soho",
      "type": "Gym",
      "address": "Dufour's Pl",
      "hours": "Closed ⋅ Opens 6 am Mon"
    },
    {
      "position": 8,
      "rating": 4.7,
      "reviews": 1300,
      "reviews_original": "(1.3K)",
      "description": "\"Great gym, super clean, nice staff, and the classes booking system is smart.\"",
      "lsig": "AB86z5U-CFhtyv9y7krMmzeFXW9l",
      "links": {
        "website": "https://www.thirdspace.london/clubs/tower-bridge/",
        "directions": "https://www.google.com/maps/dir//Third+Space+Tower+Bridge,+2b+More+London+Pl,+London+SE1+2AP/data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x4876036838efbd55:0x80936ddf7a5eb6fe?sa=X&ved=2ahUKEwjn7Y31yJKPAxUsFFkFHb4OLEAQ48ADegQIEBAA&hl=en&gl=uk"
      },
      "place_id": "9264869665029404414",
      "place_id_search": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&ludocid=9264869665029404414&q=Gym+London+UK",
      "gps_coordinates": {
        "latitude": 51.505363,
        "longitude": -0.0798011
      },
      "title": "Third Space Tower Bridge",
      "type": "Gym",
      "years_in_business": "10+ years in business",
      "address": "2b More London Pl",
      "phone": "020 7940 4937",
      "hours": "Closed ⋅ Opens 6 am Mon"
    },
    {
      "position": 9,
      "rating": 4.4,
      "reviews": 1000,
      "reviews_original": "(1K)",
      "description": "\"Great gym, excellent equipment and friendly staff.\"",
      "lsig": "AB86z5XS32jyxmyU-aD2opM2lHIN",
      "links": {
        "website": "https://www.fitnessfirst.co.uk/find-a-gym/london-baker-street?utm_campaign=gmb&utm_medium=organic&utm_source=local",
        "directions": "https://www.google.com/maps/dir//Fitness+First,+55+Baker+St,+London+W1U+8EW/data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x48761acc49bc1bed:0x9191ec859114f53c?sa=X&ved=2ahUKEwjn7Y31yJKPAxUsFFkFHb4OLEAQ48ADegQIERAA&hl=en&gl=uk"
      },
      "place_id": "10489425065531471164",
      "place_id_search": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&ludocid=10489425065531471164&q=Gym+London+UK",
      "gps_coordinates": {
        "latitude": 51.518585,
        "longitude": -0.1561806
      },
      "title": "Fitness First",
      "type": "Gym",
      "years_in_business": "10+ years in business",
      "address": "55 Baker St",
      "phone": "020 8618 3099",
      "hours": "Closed ⋅ Opens 5 am Mon"
    },
    {
      "position": 10,
      "rating": 4.7,
      "reviews": 1000,
      "reviews_original": "(1K)",
      "description": "\"Great gym with a variety of equipment, friendly staff, and clean facilities.\"",
      "lsig": "AB86z5U_rarBRAGHpNeTfFj_O5m5",
      "links": {
        "website": "https://www.thegymgroup.com/find-a-gym/north-london-gyms/london-caledonian-road/?utm_source=google&utm_medium=organic&utm_campaign=gmb-listing&utm_content=London%20Caledonian%20Road",
        "directions": "https://www.google.com/maps/dir//The+Gym+Group+London+Caledonian+Road,+7+Sterling+Wy.,+London+N7+9HJ/data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x48761bdec6b54f2b:0xb644d5783c0bec8?sa=X&ved=2ahUKEwjn7Y31yJKPAxUsFFkFHb4OLEAQ48ADegQIDRAA&hl=en&gl=uk"
      },
      "place_id": "820866070356213448",
      "place_id_search": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&ludocid=820866070356213448&q=Gym+London+UK",
      "gps_coordinates": {
        "latitude": 51.546497,
        "longitude": -0.1184104
      },
      "title": "The Gym Group London Caledonian Road",
      "type": "Fitness centre",
      "years_in_business": "3+ years in business",
      "address": "7 Sterling Wy.",
      "phone": "0300 303 4800",
      "hours": "Open 24 hours"
    },
    {
      "position": 11,
      "rating": 4.2,
      "reviews": 166,
      "reviews_original": "(166)",
      "description": "\"Full workout machines and a large free weight room downstairs.\"",
      "lsig": "AB86z5VktTFqbBVEx7KLFK2iA__c",
      "links": {
        "website": "http://anytimefitness.co.uk/gyms/UK-0044/st-pauls-london-england-ec4v-6de",
        "directions": "https://www.google.com/maps/dir//1,+Anytime+Fitness,+priory+court,+Pilgrim+St,+London+EC4V+6DE/data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x487604acc2ab2273:0x5e8321eaf2f2a7ab?sa=X&ved=2ahUKEwjn7Y31yJKPAxUsFFkFHb4OLEAQ48ADegQICxAA&hl=en&gl=uk"
      },
      "place_id": "6810324354496374699",
      "place_id_search": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&ludocid=6810324354496374699&q=Gym+London+UK",
      "gps_coordinates": {
        "latitude": 51.513676,
        "longitude": -0.102052
      },
      "title": "Anytime Fitness",
      "type": "Gym",
      "years_in_business": "10+ years in business",
      "address": "1, priory court, Pilgrim St",
      "phone": "020 3137 6489",
      "hours": "Open 24 hours"
    },
    {
      "position": 12,
      "rating": 4.9,
      "reviews": 107,
      "reviews_original": "(107)",
      "description": "\"Great gym very clean, and friendly staff!\"",
      "lsig": "AB86z5WP7KHmEqd0w2-jq3puVJZc",
      "links": {
        "website": "https://www.cityathletic.co.uk/",
        "directions": "https://www.google.com/maps/dir//City+Athletic,+20+Palace+St,+London+SW1E+5BA/data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x487605a22ae63077:0x3cafdcdaa52108d5?sa=X&ved=2ahUKEwjn7Y31yJKPAxUsFFkFHb4OLEAQ48ADegQIDBAA&hl=en&gl=uk"
      },
      "place_id": "4372956594831427797",
      "place_id_search": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&ludocid=4372956594831427797&q=Gym+London+UK",
      "gps_coordinates": {
        "latitude": 51.498043,
        "longitude": -0.1405567
      },
      "title": "City Athletic",
      "type": "Gym",
      "years_in_business": "5+ years in business",
      "address": "20 Palace St",
      "phone": "020 8076 7384",
      "hours": "Closed ⋅ Opens 6 am Mon"
    },
    {
      "position": 13,
      "rating": 4.5,
      "reviews": 937,
      "reviews_original": "(937)",
      "description": "\"Great gym, easy access, lots of equipment and plenty of showers.\"",
      "lsig": "AB86z5VyXrBIRwK7DvWsmLzwG_3V",
      "links": {
        "website": "https://www.thegymgroup.com/find-a-gym/west-london-gyms/london-paddington/?utm_source=google&utm_medium=organic&utm_campaign=gmb-listing&utm_content=London+Paddington",
        "directions": "https://www.google.com/maps/dir//The+Gym+Group+London+Paddington,+33+N+Wharf+Rd,+Merchant+Sq,+London+W2+1LA/data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x48761bb8e2dec43f:0x63537bbf57c58868?sa=X&ved=2ahUKEwjn7Y31yJKPAxUsFFkFHb4OLEAQ48ADegQIAxAA&hl=en&gl=uk"
      },
      "place_id": "7157200294563383400",
      "place_id_search": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&ludocid=7157200294563383400&q=Gym+London+UK",
      "gps_coordinates": {
        "latitude": 51.519073,
        "longitude": -0.1734289
      },
      "title": "The Gym Group London Paddington",
      "type": "Fitness centre",
      "years_in_business": "3+ years in business",
      "address": "33 N Wharf Rd, Merchant Sq",
      "phone": "0300 303 4800",
      "hours": "Open 24 hours"
    },
    {
      "position": 14,
      "rating": 4.6,
      "reviews": 605,
      "reviews_original": "(605)",
      "description": "\"Great facilities, great gym, and super helpful and friendly staff.\"",
      "lsig": "AB86z5X12L9A5KJz8uoK7TCjUuPj",
      "links": {
        "website": "https://www.fitnessfirst.co.uk/find-a-gym/london-oxford-circus?utm_campaign=gmb&utm_medium=organic&utm_source=local",
        "directions": "https://www.google.com/maps/dir//Fitness+First,+15+Great+Marlborough+St,+London+W1F+7HR/data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x487604d52e2da411:0x608c91eeb838952a?sa=X&ved=2ahUKEwjn7Y31yJKPAxUsFFkFHb4OLEAQ48ADegQIBhAA&hl=en&gl=uk"
      },
      "place_id": "6957095978859533610",
      "place_id_search": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&ludocid=6957095978859533610&q=Gym+London+UK",
      "gps_coordinates": {
        "latitude": 51.514847,
        "longitude": -0.1389095
      },
      "title": "Fitness First",
      "type": "Gym",
      "years_in_business": "10+ years in business",
      "address": "15 Great Marlborough St",
      "phone": "020 3096 7540",
      "hours": "Closed ⋅ Opens 6 am Mon"
    },
    {
      "position": 15,
      "rating": 4.6,
      "reviews": 1100,
      "reviews_original": "(1.1K)",
      "description": "\"Awesome gym Friendly staff, great classes, and clean facilities.\"",
      "lsig": "AB86z5WFJ7ZrznxIy4Ia-p4hEJge",
      "links": {
        "website": "https://www.thegymgroup.com/find-a-gym/south-london-gyms/waterloo/?utm_source=google&utm_medium=organic&utm_campaign=gmb-listing&utm_content=London%20Waterloo",
        "directions": "https://www.google.com/maps/dir//The+Gym+Group+London+Waterloo,+195-203+Waterloo+Rd,+Baron's+Pl,+London+SE1+8UX/data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x487604bb15d79e25:0x6c2b94cb4a152bf4?sa=X&ved=2ahUKEwjn7Y31yJKPAxUsFFkFHb4OLEAQ48ADegQIFBAA&hl=en&gl=uk"
      },
      "place_id": "7794487180936948724",
      "place_id_search": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&ludocid=7794487180936948724&q=Gym+London+UK",
      "gps_coordinates": {
        "latitude": 51.50082,
        "longitude": -0.1070522
      },
      "title": "The Gym Group London Waterloo",
      "type": "Fitness centre",
      "years_in_business": "10+ years in business",
      "address": "195-203 Waterloo Rd, Baron's Pl",
      "phone": "0300 303 4800",
      "hours": "Open 24 hours"
    },
    {
      "position": 16,
      "rating": 4.7,
      "reviews": 284,
      "reviews_original": "(284)",
      "description": "\"Great gym, vast array of equipment, friendly & helpful staff.\"",
      "lsig": "AB86z5WWnZUy5-tUajZ3ph2_-teF",
      "links": {
        "website": "https://www.anytimefitness.co.uk/gyms/uk-0193/london-euston-greater-london-nw1-2da/",
        "directions": "https://www.google.com/maps/dir//Anytime+Fitness+Euston,+210+Euston+Rd.,+London+NW1+2DA/data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x48761b8ff376fad1:0x586bc37700140d2a?sa=X&ved=2ahUKEwjn7Y31yJKPAxUsFFkFHb4OLEAQ48ADegQIBxAA&hl=en&gl=uk"
      },
      "place_id": "6371401013715537194",
      "place_id_search": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&ludocid=6371401013715537194&q=Gym+London+UK",
      "gps_coordinates": {
        "latitude": 51.52598,
        "longitude": -0.1359072
      },
      "title": "Anytime Fitness Euston",
      "type": "Gym",
      "address": "210 Euston Rd.",
      "phone": "020 3089 3444",
      "hours": "Open 24 hours"
    },
    {
      "position": 17,
      "rating": 4.9,
      "reviews": 63,
      "reviews_original": "(63)",
      "description": "\"The gym is private, clean, with a very good atmosphere.\"",
      "lsig": "AB86z5VWqzj9ENKgcWAymZMw5kCz",
      "links": {
        "website": "http://www.londonwellnessstudio.com/",
        "directions": "https://www.google.com/maps/dir//London+Wellness+Studio,+40+Bell+St,+London+NW1+5AW/data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x48761b0c432627cf:0x27cf6df4f6bd4884?sa=X&ved=2ahUKEwjn7Y31yJKPAxUsFFkFHb4OLEAQ48ADegQICBAA&hl=en&gl=uk",
        "schedule": "https://www.treatwell.co.uk/place/london-wellness-studio/?utm_source=google&utm_medium=rwg&hl=en-GB&gei=LiyiaOeeCqyo5NoPvp2wgQQ&rwg_token=ACgRB3eFhXYXJHutI9EIyabRNXOf8JwaqT1oxip5WprS7TEVrFyaLx9tlmSu9bXTlU7eCEdgPJ8cD1aMV5ImT2M_84lLjFlY5w%3D%3D&source=cat"
      },
      "place_id": "2868632386537343108",
      "place_id_search": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&ludocid=2868632386537343108&q=Gym+London+UK",
      "gps_coordinates": {
        "latitude": 51.52123,
        "longitude": -0.1688344
      },
      "title": "London Wellness Studio",
      "type": "Gym",
      "years_in_business": "15+ years in business",
      "address": "40 Bell St",
      "phone": "020 3859 2553",
      "hours": "Open 24 hours"
    },
    {
      "position": 18,
      "rating": 4.5,
      "reviews": 872,
      "reviews_original": "(872)",
      "description": "\"The gym is a nice, clean environment and has all the equipment needed.\"",
      "lsig": "AB86z5VPAqa_l2yFct5NbAMKhy0V",
      "links": {
        "website": "https://www.thegymgroup.com/find-a-gym/north-london-gyms/bloomsbury/?utm_source=google&utm_medium=organic&utm_campaign=gmb-listing&utm_content=London%20Bloomsbury",
        "directions": "https://www.google.com/maps/dir//The+Gym+Group+London+Bloomsbury,+Coram+St,+London+WC1N+1HB/data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x48761b30956c2957:0x8e373d4e4437748a?sa=X&ved=2ahUKEwjn7Y31yJKPAxUsFFkFHb4OLEAQ48ADegQIBRAA&hl=en&gl=uk"
      },
      "place_id": "10247726883466081418",
      "place_id_search": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&ludocid=10247726883466081418&q=Gym+London+UK",
      "gps_coordinates": {
        "latitude": 51.52424,
        "longitude": -0.1248949
      },
      "title": "The Gym Group London Bloomsbury",
      "type": "Fitness centre",
      "years_in_business": "7+ years in business",
      "address": "Coram St",
      "phone": "0300 303 4800",
      "hours": "Open 24 hours"
    },
    {
      "position": 19,
      "rating": 4.4,
      "reviews": 274,
      "reviews_original": "(274)",
      "description": "\"Fantastic gym — clean, well-equipped, and full of positive energy.\"",
      "lsig": "AB86z5VJJt9bt3r2jd2dpoMzqeEX",
      "links": {
        "website": "https://www.fitnessfirst.co.uk/find-a-gym/london-marylebone?utm_campaign=gmb&utm_medium=organic&utm_source=local",
        "directions": "https://www.google.com/maps/dir//Fitness+First,+Cavendish+Mews+N,+Hallam+St,+London+W1W+6LA/data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x48761b743408e4c1:0x116e0d9a894b916?sa=X&ved=2ahUKEwjn7Y31yJKPAxUsFFkFHb4OLEAQ48ADegQICRAA&hl=en&gl=uk"
      },
      "place_id": "78497268966406422",
      "place_id_search": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&ludocid=78497268966406422&q=Gym+London+UK",
      "gps_coordinates": {
        "latitude": 51.52033,
        "longitude": -0.143644
      },
      "title": "Fitness First",
      "type": "Fitness centre",
      "address": "Cavendish Mews N, Hallam St",
      "phone": "020 7436 9266",
      "hours": "Closed ⋅ Opens 6 am Mon"
    },
    {
      "position": 20,
      "rating": 4.0,
      "reviews": 92,
      "reviews_original": "(92)",
      "description": "\"Great gym super facilities and friendly and prepared team\"",
      "lsig": "AB86z5XuyXcYdpeEw8j-PJapKXkJ",
      "links": {
        "website": "https://www.equinox.com/ebyequinox?cid=gmb",
        "directions": "https://www.google.com/maps/dir//E+by+Equinox+St+James's,+12+St+James's+St,+London+SW1A+1ER/data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x487604d7a4b964ab:0xb07136e5a9444456?sa=X&ved=2ahUKEwjn7Y31yJKPAxUsFFkFHb4OLEAQ48ADegQIAhAA&hl=en&gl=uk"
      },
      "place_id": "12714003583058854998",
      "place_id_search": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&ludocid=12714003583058854998&q=Gym+London+UK",
      "gps_coordinates": {
        "latitude": 51.506115,
        "longitude": -0.1386542
      },
      "title": "E by Equinox St James's",
      "type": "Gym",
      "years_in_business": "7+ years in business",
      "address": "12 St James's St",
      "phone": "020 3884 2071",
      "hours": "Closed ⋅ Opens 6 am Mon"
    }
  ],
  "pagination": {
    "current": 1,
    "next": "https://www.google.com/search?q=Gym+London+UK&hl=en&gl=uk&start=20&tbm=lcl",
    "other_pages": {
      "2": "https://www.google.com/search?q=Gym+London+UK&hl=en&gl=uk&start=20&tbm=lcl",
      "3": "https://www.google.com/search?q=Gym+London+UK&hl=en&gl=uk&start=40&tbm=lcl",
      "4": "https://www.google.com/search?q=Gym+London+UK&hl=en&gl=uk&start=60&tbm=lcl",
      "5": "https://www.google.com/search?q=Gym+London+UK&hl=en&gl=uk&start=80&tbm=lcl"
    }
  },
  "serpapi_pagination": {
    "current": 1,
    "next_link": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&q=Gym+London+UK&start=20",
    "next": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&q=Gym+London+UK&start=20",
    "other_pages": {
      "2": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&q=Gym+London+UK&start=20",
      "3": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&q=Gym+London+UK&start=40",
      "4": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&q=Gym+London+UK&start=60",
      "5": "https://serpapi.com/search.json?device=desktop&engine=google_local&gl=uk&google_domain=google.com&hl=en&q=Gym+London+UK&start=80"
    }
  }
}
```