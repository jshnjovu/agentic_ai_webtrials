# DataStructure Returned By PageSpeed and WHOIS calls

## For Available Domain Sample
```json
{
      "domain": "se1gym.co.uk",
      "url": "http://www.se1gym.co.uk",
      "analysisTimestamp": "2025-08-21T03:10:07.531Z",
      "pageSpeed": {
        "domain": "se1gym.co.uk",
        "url": "http://www.se1gym.co.uk",
        "timestamp": "2025-08-21T03:10:07.531Z",
        "mobile": {
          "scores": {
            "performance": 100,
            "accessibility": 82,
            "bestPractices": 62,
            "seo": 91
          },
          "coreWebVitals": {
            "largestContentfulPaint": {
              "value": 1836.6888772112543,
              "displayValue": "1.8 s",
              "unit": "millisecond"
            },
            "firstInputDelay": {
              "value": 47,
              "displayValue": "50 ms",
              "unit": "millisecond"
            },
            "cumulativeLayoutShift": {
              "value": 0,
              "displayValue": "0",
              "unit": "unitless"
            },
            "firstContentfulPaint": {
              "value": 802.2335442300341,
              "displayValue": "0.8 s",
              "unit": "millisecond"
            },
            "speedIndex": {
              "value": 1354.9804405497644,
              "displayValue": "1.4 s",
              "unit": "millisecond"
            }
          },
          "serverMetrics": {
            "serverResponseTime": {
              "value": 58,
              "displayValue": "Root document took 60 ms",
              "unit": "millisecond"
            },
            "totalBlockingTime": {
              "value": 0,
              "displayValue": "0 ms",
              "unit": "millisecond"
            },
            "timeToInteractive": {
              "value": 1837.0388772112544,
              "displayValue": "1.8 s",
              "unit": "millisecond"
            }
          },
          "mobileUsability": {
            "mobileFriendly": false,
            "score": 60,
            "checks": {
              "hasViewportMetaTag": true,
              "contentSizedCorrectly": false,
              "tapTargetsAppropriateSize": false,
              "textReadable": true,
              "isResponsive": true
            },
            "issues": [
              "Content not sized correctly for viewport",
              "Tap targets too small"
            ],
            "realData": true
          },
          "opportunities": [
            {
              "title": "Initial server response time was short",
              "description": "Keep the server response time for the main document short because all other requests depend on it. [Learn more about the Time to First Byte metric](https://developer.chrome.com/docs/lighthouse/performance/time-to-first-byte/).",
              "potentialSavings": 58,
              "unit": "millisecond"
            },
            {
              "title": "Serve images in next-gen formats",
              "description": "Image formats like WebP and AVIF often provide better compression than PNG or JPEG, which means faster downloads and less data consumption. [Learn more about modern image formats](https://developer.chrome.com/docs/lighthouse/performance/uses-webp-images/).",
              "potentialSavings": 120,
              "unit": "millisecond"
            }
          ],
          "rawResponse": {
            "scores": {
              "performance": 100,
              "accessibility": 82,
              "bestPractices": 62,
              "seo": 91
            },
            "coreWebVitals": {
              "largestContentfulPaint": {
                "value": 1836.6888772112543,
                "displayValue": "1.8 s",
                "unit": "millisecond"
              },
              "firstInputDelay": {
                "value": 47,
                "displayValue": "50 ms",
                "unit": "millisecond"
              },
              "cumulativeLayoutShift": {
                "value": 0,
                "displayValue": "0",
                "unit": "unitless"
              },
              "firstContentfulPaint": {
                "value": 802.2335442300341,
                "displayValue": "0.8 s",
                "unit": "millisecond"
              },
              "speedIndex": {
                "value": 1354.9804405497644,
                "displayValue": "1.4 s",
                "unit": "millisecond"
              }
            },
            "serverMetrics": {
              "serverResponseTime": {
                "value": 58,
                "displayValue": "Root document took 60 ms",
                "unit": "millisecond"
              },
              "totalBlockingTime": {
                "value": 0,
                "displayValue": "0 ms",
                "unit": "millisecond"
              },
              "timeToInteractive": {
                "value": 1837.0388772112544,
                "displayValue": "1.8 s",
                "unit": "millisecond"
              }
            },
            "mobileUsability": {
              "mobileFriendly": false,
              "score": 60,
              "checks": {
                "hasViewportMetaTag": true,
                "contentSizedCorrectly": false,
                "tapTargetsAppropriateSize": false,
                "textReadable": true,
                "isResponsive": true
              },
              "issues": [
                "Content not sized correctly for viewport",
                "Tap targets too small"
              ],
              "realData": true
            },
            "opportunities": [
              {
                "title": "Initial server response time was short",
                "description": "Keep the server response time for the main document short because all other requests depend on it. [Learn more about the Time to First Byte metric](https://developer.chrome.com/docs/lighthouse/performance/time-to-first-byte/).",
                "potentialSavings": 58,
                "unit": "millisecond"
              },
              {
                "title": "Serve images in next-gen formats",
                "description": "Image formats like WebP and AVIF often provide better compression than PNG or JPEG, which means faster downloads and less data consumption. [Learn more about modern image formats](https://developer.chrome.com/docs/lighthouse/performance/uses-webp-images/).",
                "potentialSavings": 120,
                "unit": "millisecond"
              }
            ]
          }
        },
        "desktop": {
          "scores": {
            "performance": 99,
            "accessibility": 82,
            "bestPractices": 61,
            "seo": 91
          },
          "coreWebVitals": {
            "largestContentfulPaint": {
              "value": 685.6133111658239,
              "displayValue": "0.7 s",
              "unit": "millisecond"
            },
            "firstInputDelay": {
              "value": 124.99999999999989,
              "displayValue": "120 ms",
              "unit": "millisecond"
            },
            "cumulativeLayoutShift": {
              "value": 0.0014474920852919878,
              "displayValue": "0.001",
              "unit": "unitless"
            },
            "firstContentfulPaint": {
              "value": 241.14542710692825,
              "displayValue": "0.2 s",
              "unit": "millisecond"
            },
            "speedIndex": {
              "value": 555.9342357923265,
              "displayValue": "0.6 s",
              "unit": "millisecond"
            }
          },
          "serverMetrics": {
            "serverResponseTime": {
              "value": 101,
              "displayValue": "Root document took 100 ms",
              "unit": "millisecond"
            },
            "totalBlockingTime": {
              "value": 106.49999999999994,
              "displayValue": "110 ms",
              "unit": "millisecond"
            },
            "timeToInteractive": {
              "value": 1081.6159751481757,
              "displayValue": "1.1 s",
              "unit": "millisecond"
            }
          },
          "opportunities": [
            {
              "title": "Reduce unused JavaScript",
              "description": "Reduce unused JavaScript and defer loading scripts until they are required to decrease bytes consumed by network activity. [Learn how to reduce unused JavaScript](https://developer.chrome.com/docs/lighthouse/performance/unused-javascript/).",
              "potentialSavings": 80,
              "unit": "millisecond"
            },
            {
              "title": "Initial server response time was short",
              "description": "Keep the server response time for the main document short because all other requests depend on it. [Learn more about the Time to First Byte metric](https://developer.chrome.com/docs/lighthouse/performance/time-to-first-byte/).",
              "potentialSavings": 101,
              "unit": "millisecond"
            }
          ],
          "rawResponse": {
            "scores": {
              "performance": 99,
              "accessibility": 82,
              "bestPractices": 61,
              "seo": 91
            },
            "coreWebVitals": {
              "largestContentfulPaint": {
                "value": 685.6133111658239,
                "displayValue": "0.7 s",
                "unit": "millisecond"
              },
              "firstInputDelay": {
                "value": 124.99999999999989,
                "displayValue": "120 ms",
                "unit": "millisecond"
              },
              "cumulativeLayoutShift": {
                "value": 0.0014474920852919878,
                "displayValue": "0.001",
                "unit": "unitless"
              },
              "firstContentfulPaint": {
                "value": 241.14542710692825,
                "displayValue": "0.2 s",
                "unit": "millisecond"
              },
              "speedIndex": {
                "value": 555.9342357923265,
                "displayValue": "0.6 s",
                "unit": "millisecond"
              }
            },
            "serverMetrics": {
              "serverResponseTime": {
                "value": 101,
                "displayValue": "Root document took 100 ms",
                "unit": "millisecond"
              },
              "totalBlockingTime": {
                "value": 106.49999999999994,
                "displayValue": "110 ms",
                "unit": "millisecond"
              },
              "timeToInteractive": {
                "value": 1081.6159751481757,
                "displayValue": "1.1 s",
                "unit": "millisecond"
              }
            },
            "mobileUsability": {
              "mobileFriendly": false,
              "score": 40,
              "checks": {
                "hasViewportMetaTag": true,
                "contentSizedCorrectly": false,
                "tapTargetsAppropriateSize": false,
                "textReadable": false,
                "isResponsive": true
              },
              "issues": [
                "Content not sized correctly for viewport",
                "Tap targets too small",
                "Text too small to read"
              ],
              "realData": true
            },
            "opportunities": [
              {
                "title": "Reduce unused JavaScript",
                "description": "Reduce unused JavaScript and defer loading scripts until they are required to decrease bytes consumed by network activity. [Learn how to reduce unused JavaScript](https://developer.chrome.com/docs/lighthouse/performance/unused-javascript/).",
                "potentialSavings": 80,
                "unit": "millisecond"
              },
              {
                "title": "Initial server response time was short",
                "description": "Keep the server response time for the main document short because all other requests depend on it. [Learn more about the Time to First Byte metric](https://developer.chrome.com/docs/lighthouse/performance/time-to-first-byte/).",
                "potentialSavings": 101,
                "unit": "millisecond"
              }
            ]
          }
        },
        "errors": []
      },
      "whois": {
        "domain": "se1gym.co.uk",
        "timestamp": "2025-08-21T03:10:32.844Z",
        "whois": {
          "rawResponse": {
            "createdDate": "2025-01-17T18:05:57.234688Z",
            "updatedDate": "2025-01-26T05:43:10.674211Z",
            "expiresDate": "2026-01-17T18:05:57Z",
            "registrar": "Dynadot, LLC t/a Dynadot",
            "status": "ok",
            "ips": [],
            "nameServers": [
              "ns1.parkingcrew.net",
              "ns2.parkingcrew.net"
            ],
            "registrant": "Unknown",
            "country": "Unknown"
          },
          "parsed": {
            "createdDate": "2025-01-17T18:05:57.234688Z",
            "updatedDate": "2025-01-26T05:43:10.674211Z",
            "expiresDate": "2026-01-17T18:05:57Z",
            "registrar": "Dynadot, LLC t/a Dynadot",
            "status": "ok",
            "ips": [],
            "nameServers": [
              "ns1.parkingcrew.net",
              "ns2.parkingcrew.net"
            ],
            "registrant": "Unknown",
            "country": "Unknown"
          }
        },
        "whoisHistory": {
          "rawResponse": {
            "totalRecords": 35,
            "firstSeen": null,
            "lastVisit": null,
            "records": [],
            "note": "API returns only count, not individual records"
          },
          "parsed": {
            "totalRecords": 35,
            "firstSeen": null,
            "lastVisit": null,
            "records": [],
            "note": "API returns only count, not individual records"
          }
        },
        "domainAge": null,
        "credibility": null,
        "errors": [
          "Domain Age: WHOIS lookup failed: timeout of 10000ms exceeded"
        ]
      },
      "trustAndCRO": {
        "domain": "se1gym.co.uk",
        "url": "http://www.se1gym.co.uk",
        "timestamp": "2025-08-21T03:10:49.468Z",
        "trust": {
          "rawResponse": {
            "ssl": true,
            "securityHeaders": [],
            "domainAge": "0 years, 7 months, 7 days",
            "score": 32,
            "realData": {
              "ssl": true,
              "securityHeaders": true,
              "domainAge": true
            },
            "warnings": []
          },
          "parsed": {
            "score": 32,
            "ssl": true,
            "securityHeaders": [],
            "domainAge": "0 years, 7 months, 7 days",
            "realData": {
              "ssl": true,
              "securityHeaders": true,
              "domainAge": true
            },
            "warnings": []
          }
        },
        "cro": {
          "rawResponse": {
            "mobileFriendly": false,
            "mobileUsabilityScore": 60,
            "mobileIssues": [
              "Content not sized correctly for viewport",
              "Tap targets too small"
            ],
            "pageSpeed": {
              "mobile": 100,
              "desktop": 99,
              "average": 100
            },
            "userExperience": {
              "loadingTime": 100,
              "interactivity": 85,
              "visualStability": 100
            },
            "score": 88,
            "realData": true
          },
          "parsed": {
            "score": 88,
            "mobileFriendly": false,
            "mobileUsabilityScore": 60,
            "mobileIssues": [
              "Content not sized correctly for viewport",
              "Tap targets too small"
            ],
            "pageSpeed": {
              "mobile": 100,
              "desktop": 99,
              "average": 100
            },
            "userExperience": {
              "loadingTime": 100,
              "interactivity": 85,
              "visualStability": 100
            },
            "realData": true
          }
        },
        "errors": []
      },
      "uptime": {
        "domain": "se1gym.co.uk",
        "url": "http://www.se1gym.co.uk",
        "timestamp": "2025-08-21T03:11:13.112Z",
        "uptime": {
          "rawResponse": {
            "score": 100,
            "uptime": "100.0%",
            "averageResponseTime": 442,
            "status": "up",
            "realData": true
          },
          "parsed": {
            "score": 100,
            "uptime": "100.0%",
            "averageResponseTime": 442,
            "status": "up",
            "realData": true
          }
        },
        "errors": []
      },
      "summary": {
        "totalErrors": 1,
        "servicesCompleted": 4,
        "analysisDuration": 68907
      }
    }
```

For Unvalable Domains Sample

```json
 {
      "domain": "thethirdspace.com",
      "url": "http://www.thethirdspace.com",
      "analysisTimestamp": "2025-08-21T03:11:21.439Z",
      "pageSpeed": {
        "domain": "thethirdspace.com",
        "url": "http://www.thethirdspace.com",
        "timestamp": "2025-08-21T03:11:21.439Z",
        "mobile": null,
        "desktop": null,
        "errors": [
          "Mobile: PageSpeed API error: Request failed with status 400: Bad Request",
          "Desktop: PageSpeed API error: Request failed with status 400: Bad Request"
        ]
      },
      "whois": {
        "domain": "thethirdspace.com",
        "timestamp": "2025-08-21T03:12:01.472Z",
        "whois": null,
        "whoisHistory": null,
        "domainAge": null,
        "credibility": null,
        "errors": [
          "WHOIS: WHOIS lookup failed: timeout of 10000ms exceeded",
          "WHOIS History: Cannot read properties of null (reading 'totalRecords')",
          "Domain Age: WHOIS lookup failed: timeout of 10000ms exceeded"
        ]
      },
      "trustAndCRO": {
        "domain": "thethirdspace.com",
        "url": "http://www.thethirdspace.com",
        "timestamp": "2025-08-21T03:12:31.491Z",
        "trust": {
          "rawResponse": {
            "ssl": false,
            "securityHeaders": [],
            "domainAge": "25 years, 7 months, 8 days",
            "score": 15,
            "realData": {
              "ssl": true,
              "securityHeaders": true,
              "domainAge": true
            },
            "warnings": [
              "SSL check failed: timeout of 10000ms exceeded",
              "Security headers check failed: timeout of 10000ms exceeded"
            ]
          },
          "parsed": {
            "score": 15,
            "ssl": false,
            "securityHeaders": [],
            "domainAge": "25 years, 7 months, 8 days",
            "realData": {
              "ssl": true,
              "securityHeaders": true,
              "domainAge": true
            },
            "warnings": [
              "SSL check failed: timeout of 10000ms exceeded",
              "Security headers check failed: timeout of 10000ms exceeded"
            ]
          }
        },
        "cro": null,
        "errors": [
          "CRO: CRO analysis error: PageSpeed API error: Request failed with status 400: Bad Request"
        ]
      },
      "uptime": {
        "domain": "thethirdspace.com",
        "url": "http://www.thethirdspace.com",
        "timestamp": "2025-08-21T03:13:23.198Z",
        "uptime": {
          "rawResponse": {
            "score": 0,
            "uptime": "0.0%",
            "averageResponseTime": 10000,
            "status": "down",
            "realData": true
          },
          "parsed": {
            "score": 0,
            "uptime": "0.0%",
            "averageResponseTime": 10000,
            "status": "down",
            "realData": true
          }
        },
        "errors": []
      },
      "summary": {
        "totalErrors": 6,
        "servicesCompleted": -1,
        "analysisDuration": 153776
      }
    }
```