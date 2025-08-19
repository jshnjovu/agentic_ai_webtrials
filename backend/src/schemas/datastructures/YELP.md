curl "https://api.yelp.com/v3/businesses/search?term=Gym&location=London%2C%20UK&limit=10" \
  -H "Authorization: Bearer YOUR_YELP_API_KEY" \
  -H "Content-Type: application/json" | jq

```json
{
  "businesses": [
    {
      "id": "wtz-huHYAhAy0F4eenFZng",
      "alias": "the-circle-spa-london-2",
      "name": "The Circle SPA",
      "image_url": "https://s3-media0.fl.yelpcdn.com/bphoto/c8382HdImMRFpJchq2LHSw/o.jpg",
      "is_closed": false,
      "url": "https://www.yelp.com/biz/the-circle-spa-london-2?adjust_creative=0lEg8m_6goF0-hsA0TH6nw&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=0lEg8m_6goF0-hsA0TH6nw",
      "review_count": 13,
      "categories": [
        {
          "alias": "gyms",
          "title": "Gyms"
        },
        {
          "alias": "spas",
          "title": "Day Spas"
        }
      ],
      "rating": 4.6,
      "coordinates": {
        "latitude": 51.501607,
        "longitude": -0.0743388
      },
      "transactions": [],
      "price": "££££",
      "location": {
        "address1": "Queen Elizabeth Street",
        "address2": "",
        "address3": "",
        "city": "London",
        "zip_code": "SE1 2JE",
        "country": "GB",
        "state": "XGL",
        "display_address": [
          "Queen Elizabeth Street",
          "London SE1 2JE",
          "United Kingdom"
        ]
      },
      "phone": "+442073787112",
      "display_phone": "+44 20 7378 7112",
      "distance": 4477.39461558229,
      "business_hours": [
        {
          "open": [
            {
              "is_overnight": false,
              "start": "0630",
              "end": "2230",
              "day": 0
            },
            {
              "is_overnight": false,
              "start": "0630",
              "end": "2230",
              "day": 1
            },
            {
              "is_overnight": false,
              "start": "0630",
              "end": "2230",
              "day": 2
            },
            {
              "is_overnight": false,
              "start": "0630",
              "end": "2230",
              "day": 3
            },
            {
              "is_overnight": false,
              "start": "0630",
              "end": "2230",
              "day": 4
            },
            {
              "is_overnight": false,
              "start": "0800",
              "end": "2000",
              "day": 5
            },
            {
              "is_overnight": false,
              "start": "0800",
              "end": "2000",
              "day": 6
            }
          ],
          "hours_type": "REGULAR",
          "is_open_now": true
        }
      ],
      "attributes": {
        "business_url": "http://www.se1gym.co.uk",
        "about_this_biz_bio_photo_dict": {
          "photo_id": "_ufCrCt02px6mUhieeqkmA",
          "biz_user_id": null
        },
        "about_this_biz_business_recommendation": [],
        "business_temp_closed": null,
        "about_this_biz_bio": "Helen took over the Circle Spa / Circle Gym in 2005. \nIt's a family affair with her two sisters Kate and Lisa Managing the fitness centre.",
        "about_this_biz_bio_first_name": "Helen",
        "about_this_biz_bio_last_name": "P",
        "about_this_biz_history": "A family run Gym in SE1 London.",
        "about_this_biz_role": "Business Owner",
        "about_this_biz_specialties": "Welcome to the privately run Gym and Spa that is known as the Circle Gym & Spa. A completely new way to get energized and feel exhilarated, as you step away from work and discover the best kept secret in London SE1.\n\nIf you want to feel energized working out in our state of the art gym, get motivated by a fitness class, swim in our plush swimming pool or indulge in our latest addition, our spa area has just recently launched a new sauna, steam room and a bubbling jacuzzi. This is the perfect tonic to ease those stresses away. You can begin your personal journey of discovery into health and fitness at the Circle Gym and Spa.\n\nImagine a gym that takes care of your fitness, health and beauty needs and takes pride in standing a world away from impersonal chain style gyms.\n\nCity Trainers, our personal training team offer personalized 1-2-1 fitness training.  Specializing in all areas of fitness including Strength Training, Fat Loss, Sports Specific, Weight Training, Nutrition advice 7 more.",
        "about_this_biz_year_established": "2005",
        "accepted_cards": {
          "credit": true,
          "none": false,
          "debit": true
        },
        "bike_parking": null,
        "business_accepts_android_pay": null,
        "business_accepts_apple_pay": null,
        "business_parking": {
          "garage": false,
          "street": true,
          "lot": false,
          "valet": false
        },
        "dogs_allowed": null,
        "good_for_kids": null,
        "menu_url": null,
        "noise_level": null,
        "platform_delivery": null,
        "waitlist_reservation": null,
        "wi_fi": null
      }
    },
    {
      "id": "_xCgfcj867-uKvXdQky9qg",
      "alias": "the-third-space-london",
      "name": "The Third Space",
      "image_url": "https://s3-media0.fl.yelpcdn.com/bphoto/o80hcGvy49hnDs7miVRG6A/o.jpg",
      "is_closed": false,
      "url": "https://www.yelp.com/biz/the-third-space-london?adjust_creative=0lEg8m_6goF0-hsA0TH6nw&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=0lEg8m_6goF0-hsA0TH6nw",
      "review_count": 26,
      "categories": [
        {
          "alias": "gyms",
          "title": "Gyms"
        }
      ],
      "rating": 2.7,
      "coordinates": {
        "latitude": 51.511192,
        "longitude": -0.135579
      },
      "transactions": [],
      "location": {
        "address1": "13 Sherwood Street",
        "address2": "",
        "address3": "",
        "city": "London",
        "zip_code": "W1F 7BR",
        "country": "GB",
        "state": "XGL",
        "display_address": [
          "13 Sherwood Street",
          "London W1F 7BR",
          "United Kingdom"
        ]
      },
      "phone": "+442074396333",
      "display_phone": "+44 20 7439 6333",
      "distance": 179.32352386043667,
      "business_hours": [
        {
          "open": [
            {
              "is_overnight": false,
              "start": "0630",
              "end": "2300",
              "day": 0
            },
            {
              "is_overnight": false,
              "start": "0630",
              "end": "2300",
              "day": 1
            },
            {
              "is_overnight": false,
              "start": "0630",
              "end": "2300",
              "day": 2
            },
            {
              "is_overnight": false,
              "start": "0630",
              "end": "2300",
              "day": 3
            },
            {
              "is_overnight": false,
              "start": "0630",
              "end": "2300",
              "day": 4
            },
            {
              "is_overnight": false,
              "start": "0830",
              "end": "2030",
              "day": 5
            }
          ],
          "hours_type": "REGULAR",
          "is_open_now": true
        }
      ],
      "attributes": {
        "business_url": "http://www.thethirdspace.com",
        "about_this_biz_bio_photo_dict": null,
        "about_this_biz_business_recommendation": [],
        "business_temp_closed": null,
        "about_this_biz_bio": null,
        "about_this_biz_bio_first_name": null,
        "about_this_biz_bio_last_name": null,
        "about_this_biz_history": null,
        "about_this_biz_role": null,
        "about_this_biz_specialties": null,
        "about_this_biz_year_established": null,
        "bike_parking": false,
        "business_parking": {
          "garage": false,
          "street": false,
          "validated": false,
          "lot": false,
          "valet": false
        },
        "dogs_allowed": null,
        "good_for_kids": false,
        "platform_delivery": null,
        "waitlist_reservation": null
      }
    },
    {
      "id": "U5g4vFWYL3NI0aPUstdXmg",
      "alias": "virgin-active-woodford-green",
      "name": "Virgin Active",
      "image_url": "https://s3-media0.fl.yelpcdn.com/bphoto/nhcSKuNUUgR4Qe-VHVViOg/o.jpg",
      "is_closed": false,
      "url": "https://www.yelp.com/biz/virgin-active-woodford-green?adjust_creative=0lEg8m_6goF0-hsA0TH6nw&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=0lEg8m_6goF0-hsA0TH6nw",
      "review_count": 6,
      "categories": [
        {
          "alias": "gyms",
          "title": "Gyms"
        }
      ],
      "rating": 3.3,
      "coordinates": {
        "latitude": 51.6029722795102,
        "longitude": 0.0687074661254883
      },
      "transactions": [],
      "location": {
        "address1": "Manor Road",
        "address2": "Repton Park",
        "address3": "",
        "city": "Woodford Green",
        "zip_code": "IG8 8GN",
        "country": "GB",
        "state": "XGL",
        "display_address": [
          "Manor Road",
          "Repton Park",
          "Woodford Green IG8 8GN",
          "United Kingdom"
        ]
      },
      "phone": "+442085066300",
      "display_phone": "+44 20 8506 6300",
      "distance": 17339.127343191736,
      "business_hours": [],
      "attributes": {
        "business_url": "http://www.virginactive.co.uk",
        "about_this_biz_bio_photo_dict": null,
        "about_this_biz_business_recommendation": null,
        "business_temp_closed": null,
        "about_this_biz_bio": null,
        "about_this_biz_bio_first_name": null,
        "about_this_biz_bio_last_name": null,
        "about_this_biz_history": null,
        "about_this_biz_role": null,
        "about_this_biz_specialties": null,
        "about_this_biz_year_established": null,
        "bike_parking": null,
        "business_parking": null,
        "dogs_allowed": null,
        "good_for_kids": false,
        "platform_delivery": null,
        "waitlist_reservation": null
      }
    },
    {
      "id": "X485ZtiQkn0Jt129fdUPYw",
      "alias": "the-fitness-mosaic-london",
      "name": "The Fitness Mosaic",
      "image_url": "https://s3-media0.fl.yelpcdn.com/bphoto/d31SV0P3HdxQZqNFfQbiQg/o.jpg",
      "is_closed": false,
      "url": "https://www.yelp.com/biz/the-fitness-mosaic-london?adjust_creative=0lEg8m_6goF0-hsA0TH6nw&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=0lEg8m_6goF0-hsA0TH6nw",
      "review_count": 1,
      "categories": [
        {
          "alias": "healthtrainers",
          "title": "Trainers"
        },
        {
          "alias": "gyms",
          "title": "Gyms"
        }
      ],
      "rating": 5.0,
      "coordinates": {
        "latitude": 51.543804,
        "longitude": -0.151812
      },
      "transactions": [],
      "location": {
        "address1": "81-84 Chalk Farm Road",
        "address2": "",
        "address3": "",
        "city": "London",
        "zip_code": "NW1 8AR",
        "country": "GB",
        "state": "XGL",
        "display_address": [
          "81-84 Chalk Farm Road",
          "London NW1 8AR",
          "United Kingdom"
        ]
      },
      "phone": "+442072675544",
      "display_phone": "+44 20 7267 5544",
      "distance": 3622.6885521645154,
      "business_hours": [
        {
          "open": [
            {
              "is_overnight": false,
              "start": "0630",
              "end": "2200",
              "day": 0
            },
            {
              "is_overnight": false,
              "start": "0630",
              "end": "2200",
              "day": 1
            },
            {
              "is_overnight": false,
              "start": "0630",
              "end": "2200",
              "day": 2
            },
            {
              "is_overnight": false,
              "start": "0630",
              "end": "2200",
              "day": 3
            },
            {
              "is_overnight": false,
              "start": "0630",
              "end": "2100",
              "day": 4
            },
            {
              "is_overnight": false,
              "start": "0830",
              "end": "1800",
              "day": 5
            },
            {
              "is_overnight": false,
              "start": "0830",
              "end": "1800",
              "day": 6
            }
          ],
          "hours_type": "REGULAR",
          "is_open_now": false
        }
      ],
      "attributes": {
        "business_url": "http://www.thefitnessmosaic.com",
        "about_this_biz_bio_photo_dict": null,
        "about_this_biz_business_recommendation": [],
        "business_temp_closed": null,
        "about_this_biz_bio": null,
        "about_this_biz_bio_first_name": null,
        "about_this_biz_bio_last_name": null,
        "about_this_biz_history": null,
        "about_this_biz_role": null,
        "about_this_biz_specialties": null,
        "about_this_biz_year_established": null,
        "bike_parking": null,
        "business_parking": null,
        "dogs_allowed": null,
        "good_for_kids": null,
        "platform_delivery": null,
        "service_locations_biz_dict": null,
        "waitlist_reservation": null
      }
    },
    {
      "id": "NnS3pF3nwctDRHzSIbPw0A",
      "alias": "fitness4less-southwark-london",
      "name": "Fitness4Less Southwark",
      "image_url": "https://s3-media0.fl.yelpcdn.com/bphoto/4PSwdrOktdIcRRf2fyRd5A/o.jpg",
      "is_closed": false,
      "url": "https://www.yelp.com/biz/fitness4less-southwark-london?adjust_creative=0lEg8m_6goF0-hsA0TH6nw&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=0lEg8m_6goF0-hsA0TH6nw",
      "review_count": 12,
      "categories": [
        {
          "alias": "gyms",
          "title": "Gyms"
        }
      ],
      "rating": 4.1,
      "coordinates": {
        "latitude": 51.5045777235212,
        "longitude": -0.101437135762715
      },
      "transactions": [],
      "location": {
        "address1": "23-29 Great Suffolk Street",
        "address2": "Southwark",
        "address3": "",
        "city": "London",
        "zip_code": "SE1 0UE",
        "country": "GB",
        "state": "XGL",
        "display_address": [
          "23-29 Great Suffolk Street",
          "Southwark",
          "London SE1 0UE",
          "United Kingdom"
        ]
      },
      "phone": "",
      "display_phone": "",
      "distance": 2559.329698057618,
      "business_hours": [],
      "attributes": {
        "business_url": "http://www.fitness4less.co.uk/",
        "about_this_biz_bio_photo_dict": null,
        "about_this_biz_business_recommendation": null,
        "business_temp_closed": null,
        "about_this_biz_bio": null,
        "about_this_biz_bio_first_name": null,
        "about_this_biz_bio_last_name": null,
        "about_this_biz_history": null,
        "about_this_biz_role": null,
        "about_this_biz_specialties": null,
        "about_this_biz_year_established": null,
        "bike_parking": null,
        "business_parking": null,
        "dogs_allowed": null,
        "good_for_kids": false,
        "platform_delivery": null,
        "waitlist_reservation": null
      }
    },
    {
      "id": "pbUlCwfUT3aFqQEPncuvRQ",
      "alias": "orangetheory-fitness-london",
      "name": "Orangetheory Fitness",
      "image_url": "https://s3-media0.fl.yelpcdn.com/bphoto/IG9_aKjKD9VmygvmLih-Rg/o.jpg",
      "is_closed": false,
      "url": "https://www.yelp.com/biz/orangetheory-fitness-london?adjust_creative=0lEg8m_6goF0-hsA0TH6nw&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=0lEg8m_6goF0-hsA0TH6nw",
      "review_count": 7,
      "categories": [
        {
          "alias": "gyms",
          "title": "Gyms"
        }
      ],
      "rating": 4.1,
      "coordinates": {
        "latitude": 51.5450249,
        "longitude": -0.1034736
      },
      "transactions": [],
      "location": {
        "address1": "240 Upper Street",
        "address2": "",
        "address3": "",
        "city": "London",
        "zip_code": "N1 1RU",
        "country": "GB",
        "state": "XGL",
        "display_address": [
          "240 Upper Street",
          "London N1 1RU",
          "United Kingdom"
        ]
      },
      "phone": "+442038905875",
      "display_phone": "+44 20 3890 5875",
      "distance": 4221.082569891091,
      "business_hours": [],
      "attributes": {
        "business_url": "https://islington.orangetheoryfitness.com",
        "about_this_biz_bio_photo_dict": null,
        "about_this_biz_business_recommendation": null,
        "business_temp_closed": null,
        "about_this_biz_bio": null,
        "about_this_biz_bio_first_name": null,
        "about_this_biz_bio_last_name": null,
        "about_this_biz_history": null,
        "about_this_biz_role": null,
        "about_this_biz_specialties": null,
        "about_this_biz_year_established": null,
        "bike_parking": true,
        "business_parking": null,
        "dogs_allowed": null,
        "good_for_kids": false,
        "platform_delivery": null,
        "waitlist_reservation": null
      }
    },
    {
      "id": "3fB3uaa5iCGQuKgDkkf6aQ",
      "alias": "the-third-space-london-2",
      "name": "The Third Space",
      "image_url": "https://s3-media0.fl.yelpcdn.com/bphoto/6CNd7dwYb7Q2SiNj_MtDJQ/o.jpg",
      "is_closed": false,
      "url": "https://www.yelp.com/biz/the-third-space-london-2?adjust_creative=0lEg8m_6goF0-hsA0TH6nw&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=0lEg8m_6goF0-hsA0TH6nw",
      "review_count": 4,
      "categories": [
        {
          "alias": "gyms",
          "title": "Gyms"
        }
      ],
      "rating": 4.0,
      "coordinates": {
        "latitude": 51.5180166681051,
        "longitude": -0.150589942932129
      },
      "transactions": [],
      "location": {
        "address1": "Bulstrode Place",
        "address2": "Marylebone",
        "address3": "",
        "city": "London",
        "zip_code": "W1H 2HU",
        "country": "GB",
        "state": "XGL",
        "display_address": [
          "Bulstrode Place",
          "Marylebone",
          "London W1H 2HU",
          "United Kingdom"
        ]
      },
      "phone": "+442070426333",
      "display_phone": "+44 20 7042 6333",
      "distance": 1165.0515073978656,
      "business_hours": [
        {
          "open": [
            {
              "is_overnight": false,
              "start": "0630",
              "end": "2300",
              "day": 0
            },
            {
              "is_overnight": false,
              "start": "0630",
              "end": "2300",
              "day": 1
            },
            {
              "is_overnight": false,
              "start": "0630",
              "end": "2300",
              "day": 2
            },
            {
              "is_overnight": false,
              "start": "0630",
              "end": "2300",
              "day": 3
            },
            {
              "is_overnight": false,
              "start": "0630",
              "end": "2300",
              "day": 4
            },
            {
              "is_overnight": false,
              "start": "0800",
              "end": "2000",
              "day": 5
            }
          ],
          "hours_type": "REGULAR",
          "is_open_now": true
        }
      ],
      "attributes": {
        "business_url": "http://www.thethirdspace.com",
        "about_this_biz_bio_photo_dict": null,
        "about_this_biz_business_recommendation": null,
        "business_temp_closed": null,
        "about_this_biz_bio": null,
        "about_this_biz_bio_first_name": null,
        "about_this_biz_bio_last_name": null,
        "about_this_biz_history": null,
        "about_this_biz_role": null,
        "about_this_biz_specialties": null,
        "about_this_biz_year_established": null,
        "bike_parking": null,
        "business_parking": null,
        "dogs_allowed": null,
        "good_for_kids": false,
        "platform_delivery": null,
        "waitlist_reservation": null
      }
    },
    {
      "id": "OGoFeEZQUhWMpJlpL7J9dw",
      "alias": "puregym-london-13",
      "name": "PureGym",
      "image_url": "https://s3-media0.fl.yelpcdn.com/bphoto/IjoE9j7ITbJi92gh4phbOg/o.jpg",
      "is_closed": false,
      "url": "https://www.yelp.com/biz/puregym-london-13?adjust_creative=0lEg8m_6goF0-hsA0TH6nw&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=0lEg8m_6goF0-hsA0TH6nw",
      "review_count": 10,
      "categories": [
        {
          "alias": "gyms",
          "title": "Gyms"
        },
        {
          "alias": "healthtrainers",
          "title": "Trainers"
        }
      ],
      "rating": 3.6,
      "coordinates": {
        "latitude": 51.5391290294277,
        "longitude": -0.142857924071605
      },
      "transactions": [],
      "location": {
        "address1": "193-199 Camden High Street",
        "address2": "",
        "address3": "",
        "city": "London",
        "zip_code": "NW1 7BT",
        "country": "GB",
        "state": "XGL",
        "display_address": [
          "193-199 Camden High Street",
          "London NW1 7BT",
          "United Kingdom"
        ]
      },
      "phone": "+443454811731",
      "display_phone": "+44 345 481 1731",
      "distance": 2962.4367312073614,
      "business_hours": [
        {
          "open": [
            {
              "is_overnight": true,
              "start": "0000",
              "end": "0000",
              "day": 0
            },
            {
              "is_overnight": true,
              "start": "0000",
              "end": "0000",
              "day": 1
            },
            {
              "is_overnight": true,
              "start": "0000",
              "end": "0000",
              "day": 2
            },
            {
              "is_overnight": true,
              "start": "0000",
              "end": "0000",
              "day": 3
            },
            {
              "is_overnight": true,
              "start": "0000",
              "end": "0000",
              "day": 4
            },
            {
              "is_overnight": true,
              "start": "0000",
              "end": "0000",
              "day": 5
            },
            {
              "is_overnight": true,
              "start": "0000",
              "end": "0000",
              "day": 6
            }
          ],
          "hours_type": "REGULAR",
          "is_open_now": true
        }
      ],
      "attributes": {
        "business_url": "https://www.puregym.com/gyms/london-camden/",
        "about_this_biz_bio_photo_dict": null,
        "about_this_biz_business_recommendation": [],
        "business_temp_closed": null,
        "about_this_biz_bio": null,
        "about_this_biz_bio_first_name": null,
        "about_this_biz_bio_last_name": null,
        "about_this_biz_history": null,
        "about_this_biz_role": null,
        "about_this_biz_specialties": null,
        "about_this_biz_year_established": null,
        "bike_parking": true,
        "business_parking": null,
        "dogs_allowed": null,
        "good_for_kids": false,
        "platform_delivery": null,
        "service_locations_biz_dict": null,
        "waitlist_reservation": null
      }
    },
    {
      "id": "V923JqAaacF3d7YJcYZR3A",
      "alias": "marshall-street-leisure-centre-london-2",
      "name": "Marshall Street Leisure Centre",
      "image_url": "https://s3-media0.fl.yelpcdn.com/bphoto/vXOMIqEb3c5UdMRTOXEfcg/o.jpg",
      "is_closed": false,
      "url": "https://www.yelp.com/biz/marshall-street-leisure-centre-london-2?adjust_creative=0lEg8m_6goF0-hsA0TH6nw&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=0lEg8m_6goF0-hsA0TH6nw",
      "review_count": 10,
      "categories": [
        {
          "alias": "sports_clubs",
          "title": "Sports Clubs"
        }
      ],
      "rating": 4.1,
      "coordinates": {
        "latitude": 51.5136455,
        "longitude": -0.1377036
      },
      "transactions": [],
      "location": {
        "address1": "15 Marshall Street",
        "address2": "",
        "address3": "",
        "city": "London",
        "zip_code": "W1F 7EL",
        "country": "GB",
        "state": "XGL",
        "display_address": [
          "15 Marshall Street",
          "London W1F 7EL",
          "United Kingdom"
        ]
      },
      "phone": "+443330050417",
      "display_phone": "+44 333 005 0417",
      "distance": 150.79816122702553,
      "business_hours": [
        {
          "open": [
            {
              "is_overnight": false,
              "start": "0630",
              "end": "2200",
              "day": 0
            },
            {
              "is_overnight": false,
              "start": "0630",
              "end": "2200",
              "day": 1
            },
            {
              "is_overnight": false,
              "start": "0630",
              "end": "2200",
              "day": 2
            },
            {
              "is_overnight": false,
              "start": "0630",
              "end": "2200",
              "day": 3
            },
            {
              "is_overnight": false,
              "start": "0630",
              "end": "2200",
              "day": 4
            },
            {
              "is_overnight": false,
              "start": "0800",
              "end": "2000",
              "day": 5
            },
            {
              "is_overnight": false,
              "start": "0800",
              "end": "2000",
              "day": 6
            }
          ],
          "hours_type": "REGULAR",
          "is_open_now": false
        }
      ],
      "attributes": {
        "business_url": "https://www.everyoneactive.com/centre/marshall-street-leisure-centre/",
        "about_this_biz_bio_photo_dict": null,
        "about_this_biz_business_recommendation": null,
        "business_temp_closed": null,
        "about_this_biz_bio": null,
        "about_this_biz_bio_first_name": null,
        "about_this_biz_bio_last_name": null,
        "about_this_biz_history": null,
        "about_this_biz_role": null,
        "about_this_biz_specialties": null,
        "about_this_biz_year_established": null,
        "bike_parking": null,
        "business_parking": null,
        "dogs_allowed": null,
        "good_for_kids": null,
        "platform_delivery": null,
        "waitlist_reservation": null
      }
    },
    {
      "id": "SaFsLMyGOgKnLpjYBMpCYQ",
      "alias": "muscleworks-gym-london",
      "name": "Muscleworks Gym",
      "image_url": "",
      "is_closed": false,
      "url": "https://www.yelp.com/biz/muscleworks-gym-london?adjust_creative=0lEg8m_6goF0-hsA0TH6nw&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=0lEg8m_6goF0-hsA0TH6nw",
      "review_count": 7,
      "categories": [
        {
          "alias": "gyms",
          "title": "Gyms"
        }
      ],
      "rating": 3.4,
      "coordinates": {
        "latitude": 51.5225134920258,
        "longitude": -0.0640812779829111
      },
      "transactions": [],
      "location": {
        "address1": "114 Vallance Rd",
        "address2": "",
        "address3": "Bethnal Green",
        "city": "London",
        "zip_code": "E1 5BL",
        "country": "GB",
        "state": "XGL",
        "display_address": [
          "114 Vallance Rd",
          "Bethnal Green",
          "London E1 5BL",
          "United Kingdom"
        ]
      },
      "phone": "+442072560916",
      "display_phone": "+44 20 7256 0916",
      "distance": 5088.352134002478,
      "business_hours": [
        {
          "open": [
            {
              "is_overnight": false,
              "start": "0700",
              "end": "2200",
              "day": 0
            },
            {
              "is_overnight": false,
              "start": "0700",
              "end": "2200",
              "day": 1
            },
            {
              "is_overnight": false,
              "start": "0700",
              "end": "2200",
              "day": 2
            },
            {
              "is_overnight": false,
              "start": "0700",
              "end": "2200",
              "day": 3
            },
            {
              "is_overnight": false,
              "start": "0700",
              "end": "2200",
              "day": 4
            },
            {
              "is_overnight": false,
              "start": "1000",
              "end": "1700",
              "day": 5
            },
            {
              "is_overnight": false,
              "start": "1000",
              "end": "1700",
              "day": 6
            }
          ],
          "hours_type": "REGULAR",
          "is_open_now": false
        }
      ],
      "attributes": {
        "business_url": "http://www.muscleworksgym.com",
        "about_this_biz_bio_photo_dict": null,
        "about_this_biz_business_recommendation": null,
        "business_temp_closed": null,
        "about_this_biz_bio": null,
        "about_this_biz_bio_first_name": null,
        "about_this_biz_bio_last_name": null,
        "about_this_biz_history": null,
        "about_this_biz_role": null,
        "about_this_biz_specialties": null,
        "about_this_biz_year_established": null,
        "bike_parking": null,
        "business_parking": null,
        "dogs_allowed": null,
        "good_for_kids": false,
        "platform_delivery": null,
        "waitlist_reservation": null
      }
    }
  ],
  "total": 4100,
  "region": {
    "center": {
      "longitude": -0.135955810546875,
      "latitude": 51.51283552118349
    }
  }
}
```
