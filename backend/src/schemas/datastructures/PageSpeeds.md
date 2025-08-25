# Sample Good Page Speed
curl 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=<my URL>&key=<my key>&category=performance&category=seo&category=accessibility&category=best_practices'


### For http://www.se1gym.co.uk/
```json
{
  "captchaResult": "CAPTCHA_NOT_NEEDED",
  "kind": "pagespeedonline#result",
  "id": "http://www.se1gym.co.uk/",
  "loadingExperience": {
    "initial_url": "http://www.se1gym.co.uk/"
  },
  "lighthouseResult": {
    "requestedUrl": "http://www.se1gym.co.uk/",
    "finalUrl": "http://www.se1gym.co.uk/",
    "mainDocumentUrl": "http://www.se1gym.co.uk/",
    "finalDisplayedUrl": "http://www.se1gym.co.uk/",
    "lighthouseVersion": "12.8.0",
    "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/137.0.7151.119 Safari/537.36",
    "fetchTime": "2025-08-25T19:30:21.203Z",
    "environment": {
      "networkUserAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
      "hostUserAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/137.0.7151.119 Safari/537.36",
      "benchmarkIndex": 851.5,
      "credits": {
        "axe-core": "4.10.3"
      }
    },
    "runWarnings": [],
    "configSettings": {
      "emulatedFormFactor": "desktop",
      "formFactor": "desktop",
      "locale": "en-US",
      "onlyCategories": [
        "performance",
        "accessibility",
        "best-practices",
        "seo"
      ],
      "channel": "lr"
    },
    "audits": {
      "html-xml-lang-mismatch": {
        "id": "html-xml-lang-mismatch",
        "title": "`<html>` element has an `[xml:lang]` attribute with the same base language as the `[lang]` attribute.",
        "description": "If the webpage does not specify a consistent language, then the screen reader might not announce the page's text correctly. [Learn more about the `lang` attribute](https://dequeuniversity.com/rules/axe/4.10/html-xml-lang-mismatch).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "bootup-time": {
        "id": "bootup-time",
        "title": "JavaScript execution time",
        "description": "Consider reducing the time spent parsing, compiling, and executing JS. You may find delivering smaller JS payloads helps with this. [Learn how to reduce Javascript execution time](https://developer.chrome.com/docs/lighthouse/performance/bootup-time/).",
        "score": 1,
        "scoreDisplayMode": "metricSavings",
        "displayValue": "0.8 s",
        "metricSavings": {
          "TBT": 150
        },
        "details": {
          "headings": [
            {
              "valueType": "url",
              "key": "url",
              "label": "URL"
            },
            {
              "granularity": 1,
              "label": "Total CPU Time",
              "key": "total",
              "valueType": "ms"
            },
            {
              "valueType": "ms",
              "granularity": 1,
              "key": "scripting",
              "label": "Script Evaluation"
            },
            {
              "valueType": "ms",
              "key": "scriptParseCompile",
              "label": "Script Parse",
              "granularity": 1
            }
          ],
          "items": [
            {
              "total": 308.89899999999795,
              "scriptParseCompile": 1.5889999999999991,
              "scripting": 288.923999999998,
              "url": "http://www.se1gym.co.uk/"
            },
            {
              "scriptParseCompile": 6.538,
              "total": 244.43299999999863,
              "url": "http://www.google.com/adsense/domains/caf.js?abp=1&adsdeli=true",
              "scripting": 186.50499999999886
            },
            {
              "total": 160.50299999999854,
              "scripting": 150.85399999999854,
              "scriptParseCompile": 5.727,
              "url": "https://syndicatedsearch.goog/adsense/domains/caf.js?pac=2"
            },
            {
              "scriptParseCompile": 3.0020000000000002,
              "scripting": 119.99800000000015,
              "url": "https://euob.youseasky.com/sxp/i/224f85302aa2b6ec30aac9a85da2cbf9.js",
              "total": 157.44400000000016
            },
            {
              "scripting": 1.988,
              "total": 54.303000000000146,
              "scriptParseCompile": 0,
              "url": "Unattributable"
            }
          ],
          "sortedBy": [
            "total"
          ],
          "summary": {
            "wastedMs": 765.12499999999557
          },
          "type": "table"
        },
        "numericValue": 765.12499999999557,
        "numericUnit": "millisecond"
      },
      "errors-in-console": {
        "id": "errors-in-console",
        "title": "Browser errors were logged to the console",
        "description": "Errors logged to the console indicate unresolved problems. They can come from network request failures and other browser concerns. [Learn more about this errors in console diagnostic audit](https://developer.chrome.com/docs/lighthouse/best-practices/errors-in-console/)",
        "score": 0,
        "scoreDisplayMode": "binary",
        "details": {
          "items": [
            {
              "sourceLocation": {
                "line": 0,
                "type": "source-location",
                "column": 0,
                "urlProvider": "network",
                "url": "http://www.se1gym.co.uk/munin/a/ls?t=68acb9cf&token=9c4a9c1eafd7b052958cfc9bf1bd90941639b350"
              },
              "source": "network",
              "description": "Failed to load resource: net::ERR_TIMED_OUT"
            }
          ],
          "type": "table",
          "headings": [
            {
              "valueType": "source-location",
              "label": "Source",
              "key": "sourceLocation"
            },
            {
              "valueType": "code",
              "label": "Description",
              "key": "description"
            }
          ]
        }
      },
      "non-composited-animations": {
        "id": "non-composited-animations",
        "title": "Avoid non-composited animations",
        "description": "Animations which are not composited can be janky and increase CLS. [Learn how to avoid non-composited animations](https://developer.chrome.com/docs/lighthouse/performance/non-composited-animations/)",
        "score": null,
        "scoreDisplayMode": "notApplicable",
        "metricSavings": {
          "CLS": 0
        },
        "details": {
          "items": [],
          "type": "table",
          "headings": [
            {
              "valueType": "node",
              "subItemsHeading": {
                "key": "failureReason",
                "valueType": "text"
              },
              "key": "node",
              "label": "Element"
            }
          ]
        }
      },
      "aria-prohibited-attr": {
        "id": "aria-prohibited-attr",
        "title": "Elements use only permitted ARIA attributes",
        "description": "Using ARIA attributes in roles where they are prohibited can mean that important information is not communicated to users of assistive technologies. [Learn more about prohibited ARIA roles](https://dequeuniversity.com/rules/axe/4.10/aria-prohibited-attr).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "unused-css-rules": {
        "id": "unused-css-rules",
        "title": "Reduce unused CSS",
        "description": "Reduce unused rules from stylesheets and defer CSS not used for above-the-fold content to decrease bytes consumed by network activity. [Learn how to reduce unused CSS](https://developer.chrome.com/docs/lighthouse/performance/unused-css-rules/).",
        "score": 1,
        "scoreDisplayMode": "metricSavings",
        "metricSavings": {
          "LCP": 0,
          "FCP": 0
        },
        "details": {
          "overallSavingsBytes": 0,
          "headings": [],
          "sortedBy": [
            "wastedBytes"
          ],
          "items": [],
          "debugData": {
            "type": "debugdata",
            "metricSavings": {
              "FCP": 0,
              "LCP": 0
            }
          },
          "overallSavingsMs": 0,
          "type": "opportunity"
        },
        "numericValue": 0,
        "numericUnit": "millisecond"
      },
      "duplicated-javascript": {
        "id": "duplicated-javascript",
        "title": "Remove duplicate modules in JavaScript bundles",
        "description": "Remove large, duplicate JavaScript modules from bundles to reduce unnecessary bytes consumed by network activity. ",
        "score": 1,
        "scoreDisplayMode": "metricSavings",
        "metricSavings": {
          "LCP": 0,
          "FCP": 0
        },
        "details": {
          "overallSavingsBytes": 0,
          "sortedBy": [
            "wastedBytes"
          ],
          "headings": [],
          "debugData": {
            "metricSavings": {
              "FCP": 0,
              "LCP": 0
            },
            "type": "debugdata"
          },
          "overallSavingsMs": 0,
          "items": [],
          "type": "opportunity"
        },
        "numericValue": 0,
        "numericUnit": "millisecond"
      },
      "meta-refresh": {
        "id": "meta-refresh",
        "title": "The document does not use `<meta http-equiv=\"refresh\">`",
        "description": "Users do not expect a page to refresh automatically, and doing so will move focus back to the top of the page. This may create a frustrating or confusing experience. [Learn more about the refresh meta tag](https://dequeuniversity.com/rules/axe/4.10/meta-refresh).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "js-libraries": {
        "id": "js-libraries",
        "title": "Detected JavaScript libraries",
        "description": "All front-end JavaScript libraries detected on the page. [Learn more about this JavaScript library detection diagnostic audit](https://developer.chrome.com/docs/lighthouse/best-practices/js-libraries/).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "font-display": {
        "id": "font-display",
        "title": "Ensure text remains visible during webfont load",
        "description": "Leverage the `font-display` CSS feature to ensure text is user-visible while webfonts are loading. [Learn more about `font-display`](https://developer.chrome.com/docs/lighthouse/performance/font-display/).",
        "score": 0.5,
        "scoreDisplayMode": "metricSavings",
        "details": {
          "items": [
            {
              "url": "http://d38psrni17bvxu.cloudfront.net/fonts/Port_Lligat_Slab/latin.woff2",
              "wastedMs": 30.293000221252441
            }
          ],
          "headings": [
            {
              "label": "URL",
              "key": "url",
              "valueType": "url"
            },
            {
              "label": "Est Savings",
              "key": "wastedMs",
              "valueType": "ms"
            }
          ],
          "type": "table"
        },
        "warnings": []
      },
      "image-aspect-ratio": {
        "id": "image-aspect-ratio",
        "title": "Displays images with correct aspect ratio",
        "description": "Image display dimensions should match natural aspect ratio. [Learn more about image aspect ratio](https://developer.chrome.com/docs/lighthouse/best-practices/image-aspect-ratio/).",
        "score": 1,
        "scoreDisplayMode": "binary",
        "details": {
          "headings": [
            {
              "valueType": "node",
              "key": "node"
            },
            {
              "label": "URL",
              "key": "url",
              "valueType": "url"
            },
            {
              "label": "Aspect Ratio (Displayed)",
              "valueType": "text",
              "key": "displayedAspectRatio"
            },
            {
              "valueType": "text",
              "label": "Aspect Ratio (Actual)",
              "key": "actualAspectRatio"
            }
          ],
          "items": [],
          "type": "table"
        }
      },
      "empty-heading": {
        "id": "empty-heading",
        "title": "All heading elements contain content.",
        "description": "A heading with no content or inaccessible text prevent screen reader users from accessing information on the page's structure. [Learn more about headings](https://dequeuniversity.com/rules/axe/4.10/empty-heading).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "meta-viewport": {
        "id": "meta-viewport",
        "title": "`[user-scalable=\"no\"]` is not used in the `<meta name=\"viewport\">` element and the `[maximum-scale]` attribute is not less than 5.",
        "description": "Disabling zooming is problematic for users with low vision who rely on screen magnification to properly see the contents of a web page. [Learn more about the viewport meta tag](https://dequeuniversity.com/rules/axe/4.10/meta-viewport).",
        "score": 1,
        "scoreDisplayMode": "binary",
        "details": {
          "headings": [
            {
              "subItemsHeading": {
                "key": "relatedNode",
                "valueType": "node"
              },
              "label": "Failing Elements",
              "key": "node",
              "valueType": "node"
            }
          ],
          "items": [],
          "type": "table"
        }
      },
      "object-alt": {
        "id": "object-alt",
        "title": "`<object>` elements have alternate text",
        "description": "Screen readers cannot translate non-text content. Adding alternate text to `<object>` elements helps screen readers convey meaning to users. [Learn more about alt text for `object` elements](https://dequeuniversity.com/rules/axe/4.10/object-alt).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "aria-required-attr": {
        "id": "aria-required-attr",
        "title": "`[role]`s have all required `[aria-*]` attributes",
        "description": "Some ARIA roles have required attributes that describe the state of the element to screen readers. [Learn more about roles and required attributes](https://dequeuniversity.com/rules/axe/4.10/aria-required-attr).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "th-has-data-cells": {
        "id": "th-has-data-cells",
        "title": "`<th>` elements and elements with `[role=\"columnheader\"/\"rowheader\"]` have data cells they describe.",
        "description": "Screen readers have features to make navigating tables easier. Ensuring table headers always refer to some set of cells may improve the experience for screen reader users. [Learn more about table headers](https://dequeuniversity.com/rules/axe/4.10/th-has-data-cells).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "identical-links-same-purpose": {
        "id": "identical-links-same-purpose",
        "title": "Identical links have the same purpose.",
        "description": "Links with the same destination should have the same description, to help users understand the link's purpose and decide whether to follow it. [Learn more about identical links](https://dequeuniversity.com/rules/axe/4.10/identical-links-same-purpose).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "inspector-issues": {
        "id": "inspector-issues",
        "title": "No issues in the `Issues` panel in Chrome Devtools",
        "description": "Issues logged to the `Issues` panel in Chrome Devtools indicate unresolved problems. They can come from network request failures, insufficient security controls, and other browser concerns. Open up the Issues panel in Chrome DevTools for more details on each issue.",
        "score": 1,
        "scoreDisplayMode": "binary",
        "details": {
          "headings": [
            {
              "valueType": "text",
              "key": "issueType",
              "subItemsHeading": {
                "valueType": "url",
                "key": "url"
              },
              "label": "Issue type"
            }
          ],
          "type": "table",
          "items": []
        }
      },
      "link-name": {
        "id": "link-name",
        "title": "Links have a discernible name",
        "description": "Link text (and alternate text for images, when used as links) that is discernible, unique, and focusable improves the navigation experience for screen reader users. [Learn how to make links accessible](https://dequeuniversity.com/rules/axe/4.10/link-name).",
        "score": 1,
        "scoreDisplayMode": "binary",
        "details": {
          "headings": [
            {
              "subItemsHeading": {
                "valueType": "node",
                "key": "relatedNode"
              },
              "label": "Failing Elements",
              "key": "node",
              "valueType": "node"
            }
          ],
          "items": [],
          "type": "table"
        }
      },
      "trusted-types-xss": {
        "id": "trusted-types-xss",
        "title": "Mitigate DOM-based XSS with Trusted Types",
        "description": "The `require-trusted-types-for` directive in the `Content-Security-Policy` (CSP) header instructs user agents to control the data passed to DOM XSS sink functions. [Learn more about mitigating DOM-based XSS with Trusted Types](https://developer.chrome.com/docs/lighthouse/best-practices/trusted-types-xss).",
        "score": 1,
        "scoreDisplayMode": "informative",
        "details": {
          "type": "table",
          "headings": [
            {
              "subItemsHeading": {
                "key": "description"
              },
              "valueType": "text",
              "key": "description",
              "label": "Description"
            },
            {
              "subItemsHeading": {
                "key": "severity"
              },
              "label": "Severity",
              "valueType": "text",
              "key": "severity"
            }
          ],
          "items": [
            {
              "severity": "High",
              "description": "No `Content-Security-Policy` header with Trusted Types directive found"
            }
          ]
        }
      },
      "list": {
        "id": "list",
        "title": "Lists contain only `<li>` elements and script supporting elements (`<script>` and `<template>`).",
        "description": "Screen readers have a specific way of announcing lists. Ensuring proper list structure aids screen reader output. [Learn more about proper list structure](https://dequeuniversity.com/rules/axe/4.10/list).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "resource-summary": {
        "id": "resource-summary",
        "title": "Resources Summary",
        "description": "Aggregates all network requests and groups them by type",
        "score": 1,
        "scoreDisplayMode": "informative",
        "details": {
          "type": "table",
          "items": [
            {
              "requestCount": 28,
              "label": "Total",
              "resourceType": "total",
              "transferSize": 279276
            },
            {
              "requestCount": 8,
              "label": "Script",
              "transferSize": 215719,
              "resourceType": "script"
            },
            {
              "transferSize": 26158,
              "resourceType": "document",
              "label": "Document",
              "requestCount": 3
            },
            {
              "label": "Image",
              "transferSize": 16660,
              "requestCount": 9,
              "resourceType": "image"
            },
            {
              "requestCount": 1,
              "transferSize": 11993,
              "label": "Font",
              "resourceType": "font"
            },
            {
              "label": "Other",
              "requestCount": 7,
              "resourceType": "other",
              "transferSize": 8746
            },
            {
              "transferSize": 0,
              "requestCount": 0,
              "resourceType": "stylesheet",
              "label": "Stylesheet"
            },
            {
              "resourceType": "media",
              "transferSize": 0,
              "label": "Media",
              "requestCount": 0
            },
            {
              "label": "Third-party",
              "transferSize": 270432,
              "resourceType": "third-party",
              "requestCount": 24
            }
          ],
          "headings": [
            {
              "key": "label",
              "valueType": "text",
              "label": "Resource Type"
            },
            {
              "label": "Requests",
              "key": "requestCount",
              "valueType": "numeric"
            },
            {
              "valueType": "bytes",
              "label": "Transfer Size",
              "key": "transferSize"
            }
          ]
        }
      },
      "redirects": {
        "id": "redirects",
        "title": "Avoid multiple page redirects",
        "description": "Redirects introduce additional delays before the page can be loaded. [Learn how to avoid page redirects](https://developer.chrome.com/docs/lighthouse/performance/redirects/).",
        "score": 1,
        "scoreDisplayMode": "metricSavings",
        "metricSavings": {
          "LCP": 0,
          "FCP": 0
        },
        "details": {
          "items": [],
          "type": "opportunity",
          "overallSavingsMs": 0,
          "headings": []
        },
        "numericValue": 0,
        "numericUnit": "millisecond"
      },
      "aria-input-field-name": {
        "id": "aria-input-field-name",
        "title": "ARIA input fields have accessible names",
        "description": "When an input field doesn't have an accessible name, screen readers announce it with a generic name, making it unusable for users who rely on screen readers. [Learn more about input field labels](https://dequeuniversity.com/rules/axe/4.10/aria-input-field-name).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "unsized-images": {
        "id": "unsized-images",
        "title": "Image elements have explicit `width` and `height`",
        "description": "Set an explicit width and height on image elements to reduce layout shifts and improve CLS. [Learn how to set image dimensions](https://web.dev/articles/optimize-cls#images_without_dimensions)",
        "score": 1,
        "scoreDisplayMode": "metricSavings",
        "metricSavings": {
          "CLS": 0
        },
        "details": {
          "headings": [
            {
              "valueType": "node",
              "key": "node"
            },
            {
              "label": "URL",
              "key": "url",
              "valueType": "url"
            }
          ],
          "items": [],
          "type": "table"
        }
      },
      "link-text": {
        "id": "link-text",
        "title": "Links have descriptive text",
        "description": "Descriptive link text helps search engines understand your content. [Learn how to make links more accessible](https://developer.chrome.com/docs/lighthouse/seo/link-text/).",
        "score": 1,
        "scoreDisplayMode": "binary",
        "details": {
          "type": "table",
          "headings": [
            {
              "label": "Link destination",
              "valueType": "url",
              "key": "href"
            },
            {
              "label": "Link Text",
              "valueType": "text",
              "key": "text"
            }
          ],
          "items": []
        }
      },
      "unused-javascript": {
        "id": "unused-javascript",
        "title": "Reduce unused JavaScript",
        "description": "Reduce unused JavaScript and defer loading scripts until they are required to decrease bytes consumed by network activity. [Learn how to reduce unused JavaScript](https://developer.chrome.com/docs/lighthouse/performance/unused-javascript/).",
        "score": 0,
        "scoreDisplayMode": "metricSavings",
        "displayValue": "Est savings of 70 KiB",
        "metricSavings": {
          "LCP": 50,
          "FCP": 0
        },
        "details": {
          "items": [
            {
              "totalBytes": 57549,
              "wastedPercent": 69.999747446048161,
              "wastedBytes": 40284,
              "url": "https://syndicatedsearch.goog/adsense/domains/caf.js?pac=2"
            },
            {
              "totalBytes": 57677,
              "url": "http://www.google.com/adsense/domains/caf.js?abp=1&adsdeli=true",
              "wastedPercent": 55.253055864228706,
              "wastedBytes": 31868
            }
          ],
          "overallSavingsMs": 40,
          "headings": [
            {
              "key": "url",
              "valueType": "url",
              "subItemsHeading": {
                "key": "source",
                "valueType": "code"
              },
              "label": "URL"
            },
            {
              "subItemsHeading": {
                "key": "sourceBytes"
              },
              "key": "totalBytes",
              "label": "Transfer Size",
              "valueType": "bytes"
            },
            {
              "key": "wastedBytes",
              "label": "Est Savings",
              "subItemsHeading": {
                "key": "sourceWastedBytes"
              },
              "valueType": "bytes"
            }
          ],
          "overallSavingsBytes": 72152,
          "debugData": {
            "type": "debugdata",
            "metricSavings": {
              "LCP": 40,
              "FCP": 0
            }
          },
          "sortedBy": [
            "wastedBytes"
          ],
          "type": "opportunity"
        },
        "numericValue": 40,
        "numericUnit": "millisecond"
      },
      "paste-preventing-inputs": {
        "id": "paste-preventing-inputs",
        "title": "Allows users to paste into input fields",
        "description": "Preventing input pasting is a bad practice for the UX, and weakens security by blocking password managers.[Learn more about user-friendly input fields](https://developer.chrome.com/docs/lighthouse/best-practices/paste-preventing-inputs/).",
        "score": 1,
        "scoreDisplayMode": "binary",
        "details": {
          "headings": [
            {
              "valueType": "node",
              "label": "Failing Elements",
              "key": "node"
            }
          ],
          "items": [],
          "type": "table"
        }
      },
      "aria-conditional-attr": {
        "id": "aria-conditional-attr",
        "title": "ARIA attributes are used as specified for the element's role",
        "description": "Some ARIA attributes are only allowed on an element under certain conditions. [Learn more about conditional ARIA attributes](https://dequeuniversity.com/rules/axe/4.10/aria-conditional-attr).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "efficient-animated-content": {
        "id": "efficient-animated-content",
        "title": "Use video formats for animated content",
        "description": "Large GIFs are inefficient for delivering animated content. Consider using MPEG4/WebM videos for animations and PNG/WebP for static images instead of GIF to save network bytes. [Learn more about efficient video formats](https://developer.chrome.com/docs/lighthouse/performance/efficient-animated-content/)",
        "score": 1,
        "scoreDisplayMode": "metricSavings",
        "metricSavings": {
          "LCP": 0,
          "FCP": 0
        },
        "details": {
          "items": [],
          "debugData": {
            "metricSavings": {
              "FCP": 0,
              "LCP": 0
            },
            "type": "debugdata"
          },
          "overallSavingsMs": 0,
          "type": "opportunity",
          "overallSavingsBytes": 0,
          "sortedBy": [
            "wastedBytes"
          ],
          "headings": []
        },
        "numericValue": 0,
        "numericUnit": "millisecond"
      },
      "dom-size": {
        "id": "dom-size",
        "title": "Avoids an excessive DOM size",
        "description": "A large DOM will increase memory usage, cause longer [style calculations](https://developers.google.com/web/fundamentals/performance/rendering/reduce-the-scope-and-complexity-of-style-calculations), and produce costly [layout reflows](https://developers.google.com/speed/articles/reflow). [Learn how to avoid an excessive DOM size](https://developer.chrome.com/docs/lighthouse/performance/dom-size/).",
        "score": 1,
        "scoreDisplayMode": "metricSavings",
        "displayValue": "39 elements",
        "metricSavings": {
          "TBT": 0
        },
        "details": {
          "headings": [
            {
              "label": "Statistic",
              "valueType": "text",
              "key": "statistic"
            },
            {
              "label": "Element",
              "valueType": "node",
              "key": "node"
            },
            {
              "label": "Value",
              "key": "value",
              "valueType": "numeric"
            }
          ],
          "type": "table",
          "items": [
            {
              "value": {
                "value": 39,
                "type": "numeric",
                "granularity": 1
              },
              "statistic": "Total DOM Elements"
            },
            {
              "statistic": "Maximum DOM Depth",
              "node": {
                "selector": "div.wrapper3 > div.tcHolder > div#tc > iframe#master-1",
                "type": "node",
                "snippet": "<iframe frameborder=\"0\" marginwidth=\"0\" marginheight=\"0\" allowtransparency=\"true\" scrolling=\"no\" width=\"100%\" name=\"{&quot;name&quot;:&quot;master-1&quot;,&quot;slave-1-1&quot;:{&quot;clicktrackUrl&quot;:&quot;https://trkpc.net/munin/a…\" id=\"master-1\" src=\"https://syndicatedsearch.goog/afs/ads?adtest=off&amp;psid=5837883959&amp;pcsa=fals…\" allow=\"attribution-reporting\" style=\"visibility: visible; height: 498px; display: block;\">",
                "boundingRect": {
                  "top": 129,
                  "height": 498,
                  "width": 530,
                  "right": 940,
                  "left": 410,
                  "bottom": 627
                },
                "nodeLabel": "div.wrapper3 > div.tcHolder > div#tc > iframe#master-1",
                "path": "1,HTML,1,BODY,2,DIV,3,DIV,0,DIV,6,DIV,0,DIV,0,IFRAME",
                "lhId": "1-3-IFRAME"
              },
              "value": {
                "granularity": 1,
                "type": "numeric",
                "value": 7
              }
            },
            {
              "statistic": "Maximum Child Elements",
              "value": {
                "type": "numeric",
                "granularity": 1,
                "value": 10
              },
              "node": {
                "boundingRect": {
                  "right": 1350,
                  "bottom": 798,
                  "width": 1350,
                  "height": 782,
                  "top": 16,
                  "left": 0
                },
                "type": "node",
                "path": "1,HTML,1,BODY",
                "selector": "body#afd",
                "snippet": "<body id=\"afd\" style=\"visibility: visible;\">",
                "lhId": "1-1-BODY",
                "nodeLabel": "body#afd"
              }
            }
          ]
        },
        "numericValue": 39,
        "numericUnit": "element"
      },
      "third-party-cookies": {
        "id": "third-party-cookies",
        "title": "Avoids third-party cookies",
        "description": "Third-party cookies may be blocked in some contexts. [Learn more about preparing for third-party cookie restrictions](https://privacysandbox.google.com/cookies/prepare/overview).",
        "score": 1,
        "scoreDisplayMode": "binary",
        "details": {
          "type": "table",
          "items": [],
          "headings": [
            {
              "key": "name",
              "valueType": "text",
              "label": "Name"
            },
            {
              "valueType": "url",
              "key": "url",
              "label": "URL"
            }
          ]
        }
      },
      "is-crawlable": {
        "id": "is-crawlable",
        "title": "Page isn’t blocked from indexing",
        "description": "Search engines are unable to include your pages in search results if they don't have permission to crawl them. [Learn more about crawler directives](https://developer.chrome.com/docs/lighthouse/seo/is-crawlable/).",
        "score": 1,
        "scoreDisplayMode": "binary",
        "details": {
          "items": [],
          "headings": [
            {
              "key": "source",
              "label": "Blocking Directive Source",
              "valueType": "code"
            }
          ],
          "type": "table"
        },
        "warnings": []
      },
      "aria-treeitem-name": {
        "id": "aria-treeitem-name",
        "title": "ARIA `treeitem` elements have accessible names",
        "description": "When a `treeitem` element doesn't have an accessible name, screen readers announce it with a generic name, making it unusable for users who rely on screen readers. [Learn more about labeling `treeitem` elements](https://dequeuniversity.com/rules/axe/4.10/aria-treeitem-name).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "cache-insight": {
        "id": "cache-insight",
        "title": "Use efficient cache lifetimes",
        "description": "A long cache lifetime can speed up repeat visits to your page. [Learn more](https://web.dev/uses-long-cache-ttl/).",
        "score": 0,
        "scoreDisplayMode": "metricSavings",
        "displayValue": "Est savings of 46 KiB",
        "metricSavings": {
          "LCP": 50,
          "FCP": 0
        },
        "details": {
          "debugData": {
            "type": "debugdata",
            "wastedBytes": 47271.725
          },
          "headings": [
            {
              "key": "url",
              "valueType": "url",
              "label": "Request"
            },
            {
              "label": "Cache TTL",
              "key": "cacheLifetimeMs",
              "valueType": "ms",
              "displayUnit": "duration"
            },
            {
              "granularity": 1,
              "key": "totalBytes",
              "displayUnit": "kb",
              "label": "Transfer Size",
              "valueType": "bytes"
            }
          ],
          "type": "table",
          "sortedBy": [
            "wastedBytes"
          ],
          "skipSumming": [
            "cacheLifetimeMs"
          ],
          "items": [
            {
              "url": "https://euob.youseasky.com/sxp/i/224f85302aa2b6ec30aac9a85da2cbf9.js",
              "wastedBytes": 21856.5,
              "totalBytes": 43713,
              "cacheLifetimeMs": 43200000
            },
            {
              "url": "http://d38psrni17bvxu.cloudfront.net/fonts/Port_Lligat_Slab/latin.woff2",
              "totalBytes": 11993,
              "cacheLifetimeMs": 0,
              "wastedBytes": 11993
            },
            {
              "totalBytes": 11842,
              "wastedBytes": 11842,
              "cacheLifetimeMs": 0,
              "url": "http://d38psrni17bvxu.cloudfront.net/themes/cleanPeppermintBlack_657d9013/img/arrows.png"
            },
            {
              "wastedBytes": 746,
              "url": "https://partner.googleadservices.com/gampad/cookie.js?domain=www.se1gym.co.uk&client=dp-teaminternet09_3ph&product=SAS&callback=__sasCookie&cookie_types=v1%2Cv2",
              "cacheLifetimeMs": 0,
              "totalBytes": 746
            },
            {
              "cacheLifetimeMs": 82800000,
              "url": "https://afs.googleusercontent.com/ad_icons/standard/publisher_icon_image/search.svg?c=%23ffffff",
              "wastedBytes": 436.91666666666669,
              "totalBytes": 1070
            },
            {
              "wastedBytes": 397.30833333333334,
              "totalBytes": 973,
              "url": "https://afs.googleusercontent.com/ad_icons/standard/publisher_icon_image/chevron.svg?c=%23ffffff",
              "cacheLifetimeMs": 82800000
            }
          ]
        }
      },
      "interactive-element-affordance": {
        "id": "interactive-element-affordance",
        "title": "Interactive elements indicate their purpose and state",
        "description": "Interactive elements, such as links and buttons, should indicate their state and be distinguishable from non-interactive elements. [Learn how to decorate interactive elements with affordance hints](https://developer.chrome.com/docs/lighthouse/accessibility/interactive-element-affordance/).",
        "score": null,
        "scoreDisplayMode": "manual"
      },
      "third-parties-insight": {
        "id": "third-parties-insight",
        "title": "3rd parties",
        "description": "3rd party code can significantly impact load performance. [Reduce and defer loading of 3rd party code](https://web.dev/articles/optimizing-content-efficiency-loading-third-party-javascript/) to prioritize your page's content.",
        "score": 1,
        "scoreDisplayMode": "informative",
        "details": {
          "isEntityGrouped": true,
          "items": [
            {
              "entity": "Other Google APIs/SDKs",
              "transferSize": 81467,
              "mainThreadTime": 201.16397094726562,
              "subItems": {
                "type": "subitems",
                "items": [
                  {
                    "transferSize": 58391,
                    "url": "http://www.google.com/adsense/domains/caf.js?abp=1&adsdeli=true",
                    "mainThreadTime": 190.81797122955322
                  },
                  {
                    "url": "https://www.google.com/js/bg/Z-SsKYkj_Kr8t4L84tyvkiZZMnLnK5CX23Vh5jPe2Hs.js",
                    "transferSize": 23076,
                    "mainThreadTime": 10.345999717712402
                  }
                ]
              }
            },
            {
              "mainThreadTime": 156.44300079345703,
              "transferSize": 72971,
              "subItems": {
                "items": [
                  {
                    "url": "https://syndicatedsearch.goog/adsense/domains/caf.js?pac=2",
                    "transferSize": 58321,
                    "mainThreadTime": 154.35100173950195
                  },
                  {
                    "url": "https://syndicatedsearch.goog/afs/ads?adtest=off&psid=5837883959&pcsa=false&channel=000001%2Cbucket011%2Cbucket088&client=dp-teaminternet09_3ph&r=m&hl=en&rpbu=http%3A%2F%2Fwww.se1gym.co.uk%2F%3Fts%3DeyJhbGciOiJBMTI4S1ciLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0.NeKCl3434-fhnmpc7JzRjCIdVoTiSfuwVUEP2Yc-gsu0HmXc_vsFTA.6kyd_O5XT-3k6ObkEsqreg.fOjYJ2KQRB3woJ80Rozyk2zFzhL9IPaY7o0LHDPtW1pnYYwwU3Cey0UOleqiaRcI7K3h55qGWt5SDInzQbKeoYJ-RcjosmWtvgh6jfv0ah4_GTjhVamXOaufcI5E5Pv7FGXwmkt1xEO9TNeMVY7ZLZxUax-NhPw96WaiJZ0uWS3NLXuC_EuaYhmZ89c2Vw2mqMUtACT9lo-5nk4KEc47Sm9v115JGjhEmA4C9ipzAIkv1AqLse02jhlhRERJ2v0fbe3m5U3htU-fmk99vA_m1hx0e9-pcTq_CiSeuTPhtOaikysaC5k5LnEEnb01s6Ypk4i7UH7ZvegMUTLWq_8_0Elwy1KmGZFz51nQMFYvyBYAy4REN6bLeEAPvW45JVNfRBFlebEYXifkv9lt_vDqYlkSt7vFLJO8rUEOm7NXsKw-xwHuJaYp2k4urADKZnrFN8dyI04omA0wPaLcMdzI2-LQsUSbVQvDI-iWO-UWT9XkzYu97yNN7X-01fS-pRZWAkqFd_EVVqjBCwVsiinH17tDuoRZwDbxsPbs43DU4qlxXQgyp7giZeuMDKqrsDNDxCTC8fF8TKVR3tFHqurLq-7mZh_g3SE8uKEGIFwVOQREJ_l1V41r70RvpW67Twx-.nn00YuV_rZifffKjlJ4rzQ&type=3&swp=as-drid-2841604693446448&oe=UTF-8&ie=UTF-8&fexp=21404%2C17300002%2C17301437%2C17301439%2C17301442%2C17301548%2C17301266%2C72717108%2C73027842&format=r3%7Cs&nocache=1231756150223801&num=0&output=afd_ads&domain_name=www.se1gym.co.uk&v=3&bsl=8&pac=2&u_his=2&u_tz=-420&dt=1756150223803&u_w=800&u_h=600&biw=1350&bih=940&psw=1350&psh=754&frm=0&uio=--&cont=tc&drt=0&jsid=caf&nfp=1&jsv=796426389&rurl=http%3A%2F%2Fwww.se1gym.co.uk%2F",
                    "transferSize": 12658,
                    "mainThreadTime": 2.0919990539550781
                  },
                  {
                    "url": "https://syndicatedsearch.goog/afs/gen_204?client=dp-teaminternet09_3ph&output=uds_ads_only&zx=ln713idy80hw&cd_fexp=72717108%2C73027842&aqid=z7msaPCANfHZywXK5ZegAg&psid=5837883959&pbt=ri&emsg=sodar_latency&rt=1.8999996185302734&ea=10",
                    "mainThreadTime": 0,
                    "transferSize": 664
                  },
                  {
                    "transferSize": 664,
                    "mainThreadTime": 0,
                    "url": "https://syndicatedsearch.goog/afs/gen_204?client=dp-teaminternet09_3ph&output=uds_ads_only&zx=h02t5ltnisir&cd_fexp=72717108%2C73027842&aqid=z7msaPCANfHZywXK5ZegAg&psid=5837883959&pbt=bv&adbx=410&adby=129&adbh=498&adbw=530&adbah=160%2C160%2C160&adbn=master-1&eawp=partner-dp-teaminternet09_3ph&errv=796426389&csala=9%7C0%7C133%7C35%7C133&lle=0&ifv=1&hpt=1"
                  },
                  {
                    "transferSize": 664,
                    "url": "https://syndicatedsearch.goog/afs/gen_204?client=dp-teaminternet09_3ph&output=uds_ads_only&zx=4ouv3ygraqj9&cd_fexp=72717108%2C73027842&aqid=z7msaPCANfHZywXK5ZegAg&psid=5837883959&pbt=bs&adbx=410&adby=129&adbh=498&adbw=530&adbah=160%2C160%2C160&adbn=master-1&eawp=partner-dp-teaminternet09_3ph&errv=796426389&csala=9%7C0%7C133%7C35%7C133&lle=0&ifv=1&hpt=1",
                    "mainThreadTime": 0
                  }
                ],
                "type": "subitems"
              },
              "entity": "syndicatedsearch.goog"
            },
            {
              "entity": "youseasky.com",
              "subItems": {
                "items": [
                  {
                    "mainThreadTime": 132.05399513244629,
                    "transferSize": 43713,
                    "url": "https://euob.youseasky.com/sxp/i/224f85302aa2b6ec30aac9a85da2cbf9.js"
                  },
                  {
                    "mainThreadTime": 7.0830011367797852,
                    "transferSize": 1686,
                    "url": "https://obseu.youseasky.com/ct?id=80705&url=http%3A%2F%2Fwww.se1gym.co.uk%2F&sf=0&tpi=&ch=AdsDeli%20-%20domain%20-%20landingpage&uvid=9c4a9c1eafd7b052958cfc9bf1bd90941639b350&tsf=0&tsfmi=&tsfu=&cb=1756150223905&hl=2&op=0&ag=2731360679&rand=739255181577657701061820315677051408075158159128090655675510012196508605616879696829621662&fs=1350x940&fst=1350x940&np=linux%20x86_64&nv=google%20inc.&ref=&ss=800x600&nc=0&at=&di=W1siZWYiLDkyNDldLFsiYWJuY2giLDIwXSxbLTYsIntcIndcIjpbXCIwXCIsXCJ0Y2Jsb2NrXCIsXCJzZWFyY2hib3hCbG9ja1wiLFwiZ2V0WE1MaHR0cFwiLFwiYWpheFF1ZXJ5XCIsXCJhamF4QmFja2ZpbGxcIixcImxvYWRGZWVkXCIsXCJ4bWxIdHRwXCIsXCJsc1wiLFwiZ2V0TG9hZEZlZWRBcmd1bWVudHNcIixcIl9fY3RjZ19jdF84MDcwNV9leGVjXCJdLFwiblwiOltdLFwiZFwiOltdfSJdLFstNywiLSJdLFstMTIsIm51bGwiXSxbLTE4LCJbMCwwLDAsMV0iXSxbLTQ2LCIwIl0sWy01NywiV0UwWmVFdExXRUFYVkZ3WkVWRk5UVWxLQXhZV1hFeFdXeGRBVmt4S1hGaEtVa0FYV2xaVUZrcEJTUlpRRmdzTERWOEJEQW9KQzFoWUMxc1BYRm9LQ1ZoWVdnQllBUXhkV0F0YVcxOEFGMU5LQXdnRER3a0xEQTBRRlZoTkdVc1pFVkZOVFVsS0F4WVdYRXhXV3hkQVZreEtYRmhLVWtBWFdsWlVGa3BCU1JaUUZnc0xEVjhCREFvSkMxaFlDMXNQWEZvS0NWaFlXZ0JZQVF4ZFdBdGFXMThBRjFOS0F3Z0REd3dNREFBUSJdLFstNjEsIi0iXSxbLTczLCJFaFE9Il0sWy0yNCwiW10iXSxbLTEwLCItIl0sWy0xMywiLSJdLFstMiwiMTIsZWNYRlgxLzdudHZUZGxXN0s3NlNFRUNDRUpCQVJFV3VpZzBsRUlTQmNRUlVGQlFlbWhpQ0NJU3BVcUlJalNPMUlOaUNLOXBpY2tJVDJiYko5NTVkNTc3djkzM3N6Ym5Td0pJUCJdLFstMzIsIjAiXSxbLTQxLCItIl0sWy02MiwiODAiXSxbLTQsIi0iXSxbLTUsIi0iXSxbLTQ0LCIwLDAsMCw1Il0sWy05LCIrIl0sWzEyLCJ7XCJjdHhcIjpcIndlYmdsXCIsXCJ2XCI6XCJnb29nbGUgaW5jLiAoZ29vZ2xlKVwiLFwiclwiOlwiYW5nbGUgKGdvb2dsZSwgdnVsa2FuIDEuMy4wIChzd2lmdHNoYWRlciBkZXZpY2UgKHN1Ynplcm8pICgweDAwMDBjMGRlKSksIHN3aWZ0c2hhZGVyIGRyaXZlcilcIixcInNsdlwiOlwid2ViZ2wgZ2xzbCBlcyAxLjAgKG9wZW5nbCBlcyBnbHNsIGVzIDEuMCBjaHJvbWl1bSlcIixcImd2ZXJcIjpcIndlYmdsIDEuMCAob3BlbmdsIGVzIDIuMCBjaHJvbWl1bSlcIixcImd2ZW5cIjpcIndlYmtpdFwiLFwiYmVuXCI6MTAsXCJ3Z2xcIjoxLFwiZ3JlblwiOlwid2Via2l0IHdlYmdsXCIsXCJzZWZcIjoxOTMwODIwMjc5LFwic2VjXCI6XCJcIn0iXSxbLTUwLCItIl0sWy01MSwiLSJdLFstMzMsIi0iXSxbLTU2LCJsYW5kc2NhcGUtcHJpbWFyeSJdLFstMzYsIltcIjQvM1wiLFwiNC8zXCJdIl0sWy0xNiwiMCJdLFstNDgsIltcIi1cIixcIi1cIixcIi1cIixcIi1cIixcIi1cIl0iXSxbLTQ5LCItIl0sWy0yOCwiZW4tVVMiXSxbLTI5LCItIl0sWy0zMSwiZmFsc2UiXSxbLTM0LCItIl0sWy0xNCwiLSJdLFstMzUsIlsxNzU2MTUwMjIzODQxLDddIl0sWy00MiwiODgzMzk5MDE2Il0sWy02NSwiLSJdLFstNTIsIi0iXSxbLTE1LCItIl0sWy01OSwiZGVuaWVkIl0sWy0zOCwiaSwtMSwtMSwwLDAsMCwwLDAsMCwyMTg2LC0xLDAsLCwyNTQzLDI1NDQiXSxbLTYwLCItIl0sWy0yMSwiLSJdLFstMjMsIisiXSxbLTE3LCI1NiJdLFstNDAsIjMzIl0sWy02MywiMTYiXSxbLTQ1LCI2MjAsMCwwLDAsMCw1NjIsMCwwLDY0OCw1ODMsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCJdLFstMjUsIi0iXSxbLTExLCJ7XCJ0XCI6XCJcIixcIm1cIjpbXCJkZXNjcmlwdGlvblwiXX0iXSxbLTMwLCJbXCJ2XCIsMF0iXSxbLTY4LCItIl0sWy01NCwie1wiaFwiOltcIjMyOTk3Mjg0NTJcIixcIjgyMjgyMzExOVwiLFwiXzNcIixcIjI4NzI4OTkzMjBcIl0sXCJkXCI6W10sXCJiXCI6W1wiXzBcIixcIjI2NDYwMzg4MlwiXSxcInNcIjoxfSJdLFstMSwiLSJdLFstMywiW10iXSxbLTIwLCItIl0sWy00NywiQW1lcmljYS9Mb3NfQW5nZWxlcyxlbi1VUyxsYXRuLGdyZWdvcnkiXSxbLTgsIi0iXSxbLTI3LCJbMCwxMCwwLFwiNGdcIixudWxsXSJdLFstNjYsImdlb2xvY2F0aW9uLGNodWFmdWxsdmVyc2lvbmxpc3QsY3Jvc3NvcmlnaW5pc29sYXRlZCxzY3JlZW53YWtlbG9jayxwdWJsaWNrZXljcmVkZW50aWFsc2dldCxzaGFyZWRzdG9yYWdlc2VsZWN0dXJsLGNodWFhcmNoLGNvbXB1dGVwcmVzc3VyZSxjaHByZWZlcnNyZWR1Y2VkdHJhbnNwYXJlbmN5LGRlZmVycmVkZmV0Y2gsdXNiLGNoc2F2ZWRhdGEscHVibGlja2V5Y3JlZGVudGlhbHNjcmVhdGUsc2hhcmVkc3RvcmFnZSxkZWZlcnJlZGZldGNobWluaW1hbCxydW5hZGF1Y3Rpb24sY2hkb3dubGluayxjaHVhZm9ybWZhY3RvcnMsb3RwY3JlZGVudGlhbHMscGF5bWVudCxjaHVhLGNodWFtb2RlbCxjaGVjdCxhdXRvcGxheSxjYW1lcmEscHJpdmF0ZXN0YXRldG9rZW5pc3N1YW5jZSxhY2NlbGVyb21ldGVyLGNodWFwbGF0Zm9ybXZlcnNpb24saWRsZWRldGVjdGlvbixwcml2YXRlYWdncmVnYXRpb24saW50ZXJlc3Rjb2hvcnQsY2h2aWV3cG9ydGhlaWdodCxjYXB0dXJlZHN1cmZhY2Vjb250cm9sLGxvY2FsZm9udHMsY2h1YXBsYXRmb3JtLG1pZGksY2h1YWZ1bGx2ZXJzaW9uLHhyc3BhdGlhbHRyYWNraW5nLGNsaXBib2FyZHJlYWQsZ2FtZXBhZCxkaXNwbGF5Y2FwdHVyZSxrZXlib2FyZG1hcCxqb2luYWRpbnRlcmVzdGdyb3VwLGNod2lkdGgsY2hwcmVmZXJzcmVkdWNlZG1vdGlvbixicm93c2luZ3RvcGljcyxlbmNyeXB0ZWRtZWRpYSxneXJvc2NvcGUsc2VyaWFsLGNocnR0LGNodWFtb2JpbGUsd2luZG93bWFuYWdlbWVudCx1bmxvYWQsY2hkcHIsY2hwcmVmZXJzY29sb3JzY2hlbWUsY2h1YXdvdzY0LGF0dHJpYnV0aW9ucmVwb3J0aW5nLGZ1bGxzY3JlZW4saWRlbnRpdHljcmVkZW50aWFsc2dldCxwcml2YXRlc3RhdGV0b2tlbnJlZGVtcHRpb24saGlkLGNodWFiaXRuZXNzLHN0b3JhZ2VhY2Nlc3Msc3luY3hocixjaGRldmljZW1lbW9yeSxjaHZpZXdwb3J0d2lkdGgscGljdHVyZWlucGljdHVyZSxtYWduZXRvbWV0ZXIsY2xpcGJvYXJkd3JpdGUsbWljcm9waG9uZSJdLFstNjcsIi0iXSxbImJuY2giLDE3NF0sWy0zNywiLSJdLFstMzksIltcIjIwMDMwMTA3XCIsMCxcIkdlY2tvXCIsXCJOZXRzY2FwZVwiLFwiTW96aWxsYVwiLG51bGwsbnVsbCxmYWxzZSxudWxsLGZhbHNlLG51bGwsMCxmYWxzZSxmYWxzZSxudWxsLDAsZmFsc2UsZmFsc2UsZmFsc2UsdHJ1ZV0iXSxbLTQzLCIwMDAwMDAwMTAwMDAwMDAwMDAwMTEwMTEwMDAwMTEwMTAwMDAwMTAxMSJdLFstNjQsIi0iXSxbLTcwLCItIl0sWy01NSwiMCJdLFstNzQsIjAsMCJdLFstNTgsIi0iXSxbLTE5LCJbMCwwLDAsMCwwLDAsMSwyNCwyNCxcIi1cIiw4MDAsNjAwLDgwMCw2MDAsMSwxLDEzNTAsOTQwLDAsMCwwLDAsXCItXCIsXCItXCIsMTM1MCw5NDAsbnVsbF0iXSxbLTIyLCJbXCJuXCIsXCJuXCJdIl0sWy0yNiwie1widGpoc1wiOjQyMTAwMDAwLFwidWpoc1wiOjE1MjAwMDAwLFwiamhzbFwiOjM3NjAwMDAwMDB9Il0sWy02OSwiTGludXggeDg2XzY0fEdvb2dsZSBJbmMufHw1NnwtfC0iXSxbLTUzLCIwMDEiXSxbLTcxLCJhMDExMDAxMDEwMDEwMDEwMTAwMDEwMTAwMTExMTEwMTAwMDAxMCJdLFstNzIsIkV4VT0iXSxbImRkYiIsIjAsMTEsMCwwLDAsMiwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDEsMCwwLDAsMiwwLDAsMCwwLDAsMSwxLDMsMTYsMCw0LDEsMywwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMSwwLDE1LDAsMCwxLDAsMCwwLDEsMSwwLDAsMCJdLFsiY2IiLCIwLDAsMCwwLDAsMCwwLDAsMSwyLDAsMCwxMSwwLDAsNSwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMSwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMSwwLDEsMSwwLDAsMSwwLDAsMCwwLDEsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDEsMCwwLDAsMCwwLDAsMSwwLDAsMCwwLDAsMCwwLDAsMCwyLDAsMCwwLDEsMCwwLDEiXV0%3D&dep=0&pre=0&sdd=&cri=fqAne8RIw5&pto=2606&ver=65&gac=-&mei=&ap=&fe=1&duid=1.1756150223.YVG3JTEVgf9ywIYO&suid=1.1756150223.4bvPKt14TpOsCR9g&tuid=1.1756150223.xytAvRB2DNsL7K7j&fbc=-&gtm=-&it=7%2C2191%2C60&fbcl=-&gacl=-&gacsd=-&rtic=-&rtict=-&bgc=-&spa=1&urid=0&ab=&sck=-&io=aGA2Og%3D%3D"
                  },
                  {
                    "mainThreadTime": 0.053002357482910156,
                    "url": "https://obseu.youseasky.com/mon",
                    "transferSize": 774
                  },
                  {
                    "transferSize": 249,
                    "mainThreadTime": 0,
                    "url": "https://obseu.youseasky.com/tracker/tc_imp.gif?e=37dfbd8ee84e00126fe8c630ea4588999225c24f567d43d6da1908be6245cad7bd70a976750ef80ed89373bfe70e9c20c1e53e8d56118a6d2217071a10acf9f29f671f8282d8562c6b1bfd7e21578738de61ce553401279a010456640d59c0b96f4c77be26bb25cb43e2953dee536fae13246410d85afe5aecd2948a7fe07f52a13ad2a24710d14e681f2d1586d31c64e56ad2b785ba130be20ad7bc29917f9e3e9840f85473be5266e97c56052ca4482bc9d8a5e416af3db153bb46a1352837a6d2347e25795f957df2e57d8d7829e8cfe879186a5583d5757f92902f46681b2c5214a68d2a7e7d19a4e44969effaa37fd2b944771e2bb5a5a384eb2ffc82830ff62ac50f662695b7dff6a3268ccea03ed62104c3ac9c2d4c14f5356cad914265bddfaf27dd53ae4fe6d719cb4b9e9e7ec63961918b3bca3bc5c0e2f088eee01136e46af4e7e823436cf897239aab5df402011f94085bd2998c84c0f1c927c16790d0f58e7fae24287ac4682c97859c426788b821e541e6d315d6409e3d0c0b548c6eec439cd0ad3fe0d776870ce08bdbcb7789490435bd1e5a137f433e9fec40b254f2cb892fe7d127fb9d23d989e5bc32cdbee453607584ec4c47deb0491442f8eff63ff36bdeb303b1f224a022b22d870485678bf169995e5eb0bc9874222d7c117c592f4bf3b4d228ab56a54f5c5e3be4a60d838a1267fcb8c3bbbd6edeeee6fa9afbaef2574e3dfe5b87b6596d815f6307ca61596d71f472b36b18c1ebdd7e8d61d23996ad2ecda4109e7b0b3d3d057d1080dde3da3867489c184589cedfbbb2d64e039eb3d061849b36228cc0182e68e790de5327b622855d9d19fd56fd65d8b2778ddc65b492c195e12e1dfdfc2920c72ff29fbab917826d331303956d4352b3a0418bbe52aae2dfc950a9c7f8707d554ee92fb717ee10ebd57b9c20423f403d7879e05f8e833156a72789e38473bbbd4ff80a30d316072bc5facd1818ae27e7847bb1012d014abc3b3283c2ba74d9157ac39719a1c3cfabd1068b210a7144b62e7a0cfec55b05e562f5f4c3319d87b94c4f76a06a3c1a44924642ec9bf20a51cd3733c19d8541d5c6fa921b30b031b9076350ca5231209683555381d4ffc4bdf140b478b464d725dd9d5d87beba393dee8640c298b9aed6aa809826488dfa3704d82d980b985fe7ed37ba8d898c37a08c8bbda71a6786b8a58703b308d7014d3b4c3fd89a6f678026bf10&cri=fqAne8RIw5&ts=224&cb=1756150224129"
                  }
                ],
                "type": "subitems"
              },
              "transferSize": 46422,
              "mainThreadTime": 139.18999862670898
            },
            {
              "subItems": {
                "items": [
                  {
                    "mainThreadTime": 11.944000244140625,
                    "transferSize": 21934,
                    "url": "https://pagead2.googlesyndication.com/bg/qoxIykLQHporMav0XsqS8NtTd2boZuUJaM-UYWb_7aA.js"
                  },
                  {
                    "mainThreadTime": 0.88599872589111328,
                    "transferSize": 746,
                    "url": "https://partner.googleadservices.com/gampad/cookie.js?domain=www.se1gym.co.uk&client=dp-teaminternet09_3ph&product=SAS&callback=__sasCookie&cookie_types=v1%2Cv2"
                  }
                ],
                "type": "subitems"
              },
              "mainThreadTime": 12.829998970031738,
              "entity": "Google/Doubleclick Ads",
              "transferSize": 22680
            },
            {
              "entity": "adtrafficquality.google",
              "transferSize": 21014,
              "mainThreadTime": 10.744998931884766,
              "subItems": {
                "items": [
                  {
                    "transferSize": 7852,
                    "url": "https://ep2.adtrafficquality.google/sodar/sodar2.js",
                    "mainThreadTime": 6.0590009689331055
                  },
                  {
                    "url": "https://ep2.adtrafficquality.google/sodar/sodar2/237/runner.html",
                    "mainThreadTime": 4.5819978713989258,
                    "transferSize": 5732
                  },
                  {
                    "mainThreadTime": 0.10400009155273438,
                    "transferSize": 6896,
                    "url": "https://ep1.adtrafficquality.google/getconfig/sodar?sv=200&tid=afs&tv=10&st=env"
                  },
                  {
                    "transferSize": 382,
                    "url": "https://ep1.adtrafficquality.google/pagead/sodar?id=sodar2&v=237&t=2&li=afs_10&jk=0LmsaODgE9_r-cAP17iK0Qg&bg=!4OOl46zNAAbD0V7L49E7ADQBe5WfOBu12a6apHAunArmXJ_piUmk7r8CD2KxYXsGFaeoc05-zyQIlMHdOu4kFFakGVYHAgAAAMVSAAAAB2gBB34AE9k91IHfgjjLAz_ntdwV8U98_HgKAXGyDie6Xq-g4bXSzYBGDBdnEyINGYxSpauWSXNTZDkiTP6pMtI9lsyqmf5m35zsPLl70UOAxK2MDNsFY3V0xGbqkTLcWRgTVlLP6Tu2hyWkax6RHOqbX6mEmKzfhcaPXyez5YOmEdAn2EqtaMeOES58w9uLeqbHIz2JdsSXeKCa--qIxpl02fmqX95Gww6rbhr3Ix5PWrBA58LnM-JNYrG92XRHocbU8ldKDidpEL1mS9uu4HHSfnMhjnJTe-dSJE64ohWfoWUiF9THWX1UAEJYcw90nc2mP-DjuWHLfHiiG_Y4lQ7ybtWkMcWsk7iAaCPDjPq4AtoLKuAmTaZ0hYc9jgIDr5jMbZM_s4yqUFMCVMXKAsLYcXgbSE0-Q1Vh9cacXBY6cpnjLHonbYTfLSG74u6TukM4e_dElOTAT2lYmkRVjWDNvazSzNDuSDM5o0jQvodwtIL3eKJJdh8VldYa79Ploh7I9xvtWLYKmBzxFuGZAUNrV4mJvw2wWDbDaSZcowwlUwJGWXwEIHvRuUtzzvcpGyiAqs7x8WwZB8ttD473ZxQ49b5ZI2loa3PclTZr-kNezlZ3iD8Dh3LAU83dIulbf7gkWPelerrQtuhgtvGsixqI_N71A6F9uhq4Z08XwtdGTvvj_Dhb3IBN7SNn92ZqZnsjvN4NkDVdyM_yYW5IUXdiU6VBO8O2mfxTTqL7OVOdsAq9WrFiXDQEcIozkitPASBpXrg4FLX0R0fpuFl-iIs16vXABBp3fe4dMsjJTlULAKTRc_-S22XDhjduzdtYl-MYyXs4Bni-x5qYQ00fu5aT9dfvIMuAm2cg50vbbNFBssQaGCLpcRkvjpOF8HBMht26cBFi9otqsWQm9cdXs6zn8fXYLu3TTw42X25lxir73lPvKy6OGXEZCR3__s2oMrahZA",
                    "mainThreadTime": 0
                  },
                  {
                    "transferSize": 152,
                    "mainThreadTime": 0,
                    "url": "https://ep2.adtrafficquality.google/generate_204?VP_7Ww"
                  }
                ],
                "type": "subitems"
              }
            },
            {
              "transferSize": 23835,
              "subItems": {
                "items": [
                  {
                    "transferSize": 11993,
                    "mainThreadTime": 0,
                    "url": "http://d38psrni17bvxu.cloudfront.net/fonts/Port_Lligat_Slab/latin.woff2"
                  },
                  {
                    "mainThreadTime": 0,
                    "transferSize": 11842,
                    "url": "http://d38psrni17bvxu.cloudfront.net/themes/cleanPeppermintBlack_657d9013/img/arrows.png"
                  }
                ],
                "type": "subitems"
              },
              "entity": "cloudfront.net",
              "mainThreadTime": 0
            },
            {
              "mainThreadTime": 0,
              "subItems": {
                "type": "subitems",
                "items": [
                  {
                    "mainThreadTime": 0,
                    "url": "https://afs.googleusercontent.com/ad_icons/standard/publisher_icon_image/search.svg?c=%23ffffff",
                    "transferSize": 1070
                  },
                  {
                    "url": "https://afs.googleusercontent.com/ad_icons/standard/publisher_icon_image/chevron.svg?c=%23ffffff",
                    "transferSize": 973,
                    "mainThreadTime": 0
                  }
                ]
              },
              "transferSize": 2043,
              "entity": "googleusercontent.com"
            }
          ],
          "type": "table",
          "headings": [
            {
              "label": "3rd party",
              "key": "entity",
              "subItemsHeading": {
                "valueType": "url",
                "key": "url"
              },
              "valueType": "text"
            },
            {
              "subItemsHeading": {
                "key": "transferSize"
              },
              "label": "Transfer size",
              "valueType": "bytes",
              "granularity": 1,
              "key": "transferSize"
            },
            {
              "label": "Main thread time",
              "key": "mainThreadTime",
              "valueType": "ms",
              "subItemsHeading": {
                "key": "mainThreadTime"
              },
              "granularity": 1
            }
          ]
        }
      },
      "layout-shifts": {
        "id": "layout-shifts",
        "title": "Avoid large layout shifts",
        "description": "These are the largest layout shifts observed on the page. Each table item represents a single layout shift, and shows the element that shifted the most. Below each item are possible root causes that led to the layout shift. Some of these layout shifts may not be included in the CLS metric value due to [windowing](https://web.dev/articles/cls#what_is_cls). [Learn how to improve CLS](https://web.dev/articles/optimize-cls)",
        "score": 1,
        "scoreDisplayMode": "informative",
        "displayValue": "2 layout shifts found",
        "metricSavings": {
          "CLS": 0.001
        },
        "details": {
          "headings": [
            {
              "label": "Element",
              "valueType": "node",
              "key": "node",
              "subItemsHeading": {
                "key": "extra"
              }
            },
            {
              "key": "score",
              "valueType": "numeric",
              "granularity": 0.001,
              "label": "Layout shift score",
              "subItemsHeading": {
                "valueType": "text",
                "key": "cause"
              }
            }
          ],
          "items": [
            {
              "node": {
                "snippet": "<div class=\"footer\">",
                "type": "node",
                "path": "1,HTML,1,BODY,2,DIV,4,DIV",
                "boundingRect": {
                  "bottom": 798,
                  "height": 154,
                  "width": 472,
                  "left": 439,
                  "top": 644,
                  "right": 911
                },
                "selector": "body#afd > div.wrapper1 > div.footer",
                "nodeLabel": "2025 Copyright | All Rights Reserved.\n\nPrivacy Policy\n\n\n\n",
                "lhId": "page-2-DIV"
              },
              "score": 0.0014040288357703647
            },
            {
              "node": {
                "selector": "div.wrapper1 > div.sale_diagonal_top > a > span",
                "boundingRect": {
                  "width": 107,
                  "right": 1323,
                  "height": 107,
                  "top": 24,
                  "left": 1217,
                  "bottom": 130
                },
                "lhId": "page-1-SPAN",
                "snippet": "<span>",
                "path": "1,HTML,1,BODY,2,DIV,2,DIV,0,A,2,SPAN",
                "nodeLabel": "BUY THIS DOMAIN.",
                "type": "node"
              },
              "subItems": {
                "items": [
                  {
                    "cause": "Web font loaded",
                    "extra": {
                      "type": "url",
                      "value": "http://d38psrni17bvxu.cloudfront.net/fonts/Port_Lligat_Slab/latin.woff2"
                    }
                  }
                ],
                "type": "subitems"
              },
              "score": 0.000043463249521623179
            }
          ],
          "type": "table"
        }
      },
      "network-requests": {
        "id": "network-requests",
        "title": "Network Requests",
        "description": "Lists the network requests that were made during page load.",
        "score": 1,
        "scoreDisplayMode": "informative",
        "details": {
          "type": "table",
          "items": [
            {
              "experimentalFromMainFrame": true,
              "transferSize": 7768,
              "networkRequestTime": 0.82100009918212891,
              "resourceSize": 18817,
              "statusCode": 200,
              "rendererStartTime": 0,
              "url": "http://www.se1gym.co.uk/",
              "sessionTargetType": "page",
              "protocol": "http/1.1",
              "entity": "se1gym.co.uk",
              "priority": "VeryHigh",
              "mimeType": "text/html",
              "networkEndTime": 2185.5470008850098,
              "finished": true,
              "resourceType": "Document"
            },
            {
              "entity": "youseasky.com",
              "resourceSize": 117498,
              "finished": true,
              "statusCode": 200,
              "networkRequestTime": 2191.6960000991821,
              "rendererStartTime": 2190.7849998474121,
              "sessionTargetType": "page",
              "mimeType": "text/javascript",
              "experimentalFromMainFrame": true,
              "networkEndTime": 2251.5609998703003,
              "priority": "Low",
              "protocol": "h2",
              "resourceType": "Script",
              "transferSize": 43713,
              "url": "https://euob.youseasky.com/sxp/i/224f85302aa2b6ec30aac9a85da2cbf9.js"
            },
            {
              "experimentalFromMainFrame": true,
              "transferSize": 537,
              "networkEndTime": 2404.3550004959106,
              "url": "http://www.se1gym.co.uk/munin/a/tr/browserjs?domain=se1gym.co.uk&toggle=browserjs&uid=MTc1NjE1MDIyMy40NDU0OmU3YWMzYzM2OGJlODZkOTc1ZDY2NjM4ZWFmZTgzZTk3Y2YyYWUyODUxYWIwZTU3YzFlMWE0MDMxMDhmNjdlNGY6NjhhY2I5Y2Y2Y2JmMA%3D%3D",
              "statusCode": 200,
              "protocol": "http/1.1",
              "priority": "VeryHigh",
              "finished": true,
              "mimeType": "text/html",
              "networkRequestTime": 2201.7410011291504,
              "resourceSize": 0,
              "entity": "se1gym.co.uk",
              "rendererStartTime": 2200.6330003738403,
              "sessionTargetType": "page",
              "resourceType": "XHR"
            },
            {
              "networkRequestTime": 2406.923999786377,
              "experimentalFromMainFrame": true,
              "mimeType": "image/png",
              "priority": "High",
              "resourceType": "Image",
              "url": "http://d38psrni17bvxu.cloudfront.net/themes/cleanPeppermintBlack_657d9013/img/arrows.png",
              "transferSize": 11842,
              "networkEndTime": 2437.8680000305176,
              "rendererStartTime": 2406.3660001754761,
              "protocol": "http/1.1",
              "statusCode": 200,
              "sessionTargetType": "page",
              "finished": true,
              "entity": "cloudfront.net",
              "resourceSize": 11375
            },
            {
              "mimeType": "font/woff",
              "networkRequestTime": 2407.125,
              "resourceType": "Font",
              "experimentalFromMainFrame": true,
              "protocol": "http/1.1",
              "sessionTargetType": "page",
              "resourceSize": 11460,
              "transferSize": 11993,
              "priority": "VeryHigh",
              "rendererStartTime": 2406.7640008926392,
              "url": "http://d38psrni17bvxu.cloudfront.net/fonts/Port_Lligat_Slab/latin.woff2",
              "statusCode": 200,
              "entity": "cloudfront.net",
              "networkEndTime": 2437.4180002212524,
              "finished": true
            },
            {
              "statusCode": -1,
              "entity": "se1gym.co.uk",
              "url": "http://www.se1gym.co.uk/munin/a/ls?t=68acb9cf&token=9c4a9c1eafd7b052958cfc9bf1bd90941639b350",
              "sessionTargetType": "page",
              "experimentalFromMainFrame": true,
              "resourceType": "XHR",
              "rendererStartTime": 2414.3190002441406,
              "transferSize": 0,
              "networkEndTime": 6431.7980003356934,
              "resourceSize": 0,
              "networkRequestTime": 2414.3190002441406,
              "finished": true,
              "priority": "High"
            },
            {
              "protocol": "http/1.1",
              "entity": "Other Google APIs/SDKs",
              "networkRequestTime": 2416.1389999389648,
              "experimentalFromMainFrame": true,
              "resourceType": "Script",
              "mimeType": "text/javascript",
              "resourceSize": 158384,
              "finished": true,
              "statusCode": 200,
              "sessionTargetType": "page",
              "priority": "Low",
              "networkEndTime": 2430.4840002059937,
              "rendererStartTime": 2415.5950002670288,
              "url": "http://www.google.com/adsense/domains/caf.js?abp=1&adsdeli=true",
              "transferSize": 58391
            },
            {
              "resourceSize": 378,
              "priority": "Low",
              "finished": true,
              "transferSize": 746,
              "networkEndTime": 2504.1000003814697,
              "protocol": "h2",
              "networkRequestTime": 2495.0380001068115,
              "sessionTargetType": "page",
              "rendererStartTime": 2494.3240003585815,
              "experimentalFromMainFrame": true,
              "resourceType": "Script",
              "url": "https://partner.googleadservices.com/gampad/cookie.js?domain=www.se1gym.co.uk&client=dp-teaminternet09_3ph&product=SAS&callback=__sasCookie&cookie_types=v1%2Cv2",
              "statusCode": 200,
              "mimeType": "text/javascript",
              "entity": "Google/Doubleclick Ads"
            },
            {
              "resourceType": "Document",
              "statusCode": 200,
              "networkRequestTime": 2509.7230005264282,
              "entity": "syndicatedsearch.goog",
              "finished": true,
              "url": "https://syndicatedsearch.goog/afs/ads?adtest=off&psid=5837883959&pcsa=false&channel=000001%2Cbucket011%2Cbucket088&client=dp-teaminternet09_3ph&r=m&hl=en&rpbu=http%3A%2F%2Fwww.se1gym.co.uk%2F%3Fts%3DeyJhbGciOiJBMTI4S1ciLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0.NeKCl3434-fhnmpc7JzRjCIdVoTiSfuwVUEP2Yc-gsu0HmXc_vsFTA.6kyd_O5XT-3k6ObkEsqreg.fOjYJ2KQRB3woJ80Rozyk2zFzhL9IPaY7o0LHDPtW1pnYYwwU3Cey0UOleqiaRcI7K3h55qGWt5SDInzQbKeoYJ-RcjosmWtvgh6jfv0ah4_GTjhVamXOaufcI5E5Pv7FGXwmkt1xEO9TNeMVY7ZLZxUax-NhPw96WaiJZ0uWS3NLXuC_EuaYhmZ89c2Vw2mqMUtACT9lo-5nk4KEc47Sm9v115JGjhEmA4C9ipzAIkv1AqLse02jhlhRERJ2v0fbe3m5U3htU-fmk99vA_m1hx0e9-pcTq_CiSeuTPhtOaikysaC5k5LnEEnb01s6Ypk4i7UH7ZvegMUTLWq_8_0Elwy1KmGZFz51nQMFYvyBYAy4REN6bLeEAPvW45JVNfRBFlebEYXifkv9lt_vDqYlkSt7vFLJO8rUEOm7NXsKw-xwHuJaYp2k4urADKZnrFN8dyI04omA0wPaLcMdzI2-LQsUSbVQvDI-iWO-UWT9XkzYu97yNN7X-01fS-pRZWAkqFd_EVVqjBCwVsiinH17tDuoRZwDbxsPbs43DU4qlxXQgyp7giZeuMDKqrsDNDxCTC8fF8TKVR3tFHqurLq-7mZh_g3SE8uKEGIFwVOQREJ_l1V41r70RvpW67Twx-.nn00YuV_rZifffKjlJ4rzQ&type=3&swp=as-drid-2841604693446448&oe=UTF-8&ie=UTF-8&fexp=21404%2C17300002%2C17301437%2C17301439%2C17301442%2C17301548%2C17301266%2C72717108%2C73027842&format=r3%7Cs&nocache=1231756150223801&num=0&output=afd_ads&domain_name=www.se1gym.co.uk&v=3&bsl=8&pac=2&u_his=2&u_tz=-420&dt=1756150223803&u_w=800&u_h=600&biw=1350&bih=940&psw=1350&psh=754&frm=0&uio=--&cont=tc&drt=0&jsid=caf&nfp=1&jsv=796426389&rurl=http%3A%2F%2Fwww.se1gym.co.uk%2F",
              "networkEndTime": 2624.9020004272461,
              "sessionTargetType": "page",
              "mimeType": "text/html",
              "transferSize": 12658,
              "rendererStartTime": 2508.3140001296997,
              "resourceSize": 27038,
              "priority": "VeryHigh",
              "protocol": "h2"
            },
            {
              "url": "https://obseu.youseasky.com/ct?id=80705&url=http%3A%2F%2Fwww.se1gym.co.uk%2F&sf=0&tpi=&ch=AdsDeli%20-%20domain%20-%20landingpage&uvid=9c4a9c1eafd7b052958cfc9bf1bd90941639b350&tsf=0&tsfmi=&tsfu=&cb=1756150223905&hl=2&op=0&ag=2731360679&rand=739255181577657701061820315677051408075158159128090655675510012196508605616879696829621662&fs=1350x940&fst=1350x940&np=linux%20x86_64&nv=google%20inc.&ref=&ss=800x600&nc=0&at=&di=W1siZWYiLDkyNDldLFsiYWJuY2giLDIwXSxbLTYsIntcIndcIjpbXCIwXCIsXCJ0Y2Jsb2NrXCIsXCJzZWFyY2hib3hCbG9ja1wiLFwiZ2V0WE1MaHR0cFwiLFwiYWpheFF1ZXJ5XCIsXCJhamF4QmFja2ZpbGxcIixcImxvYWRGZWVkXCIsXCJ4bWxIdHRwXCIsXCJsc1wiLFwiZ2V0TG9hZEZlZWRBcmd1bWVudHNcIixcIl9fY3RjZ19jdF84MDcwNV9leGVjXCJdLFwiblwiOltdLFwiZFwiOltdfSJdLFstNywiLSJdLFstMTIsIm51bGwiXSxbLTE4LCJbMCwwLDAsMV0iXSxbLTQ2LCIwIl0sWy01NywiV0UwWmVFdExXRUFYVkZ3WkVWRk5UVWxLQXhZV1hFeFdXeGRBVmt4S1hGaEtVa0FYV2xaVUZrcEJTUlpRRmdzTERWOEJEQW9KQzFoWUMxc1BYRm9LQ1ZoWVdnQllBUXhkV0F0YVcxOEFGMU5LQXdnRER3a0xEQTBRRlZoTkdVc1pFVkZOVFVsS0F4WVdYRXhXV3hkQVZreEtYRmhLVWtBWFdsWlVGa3BCU1JaUUZnc0xEVjhCREFvSkMxaFlDMXNQWEZvS0NWaFlXZ0JZQVF4ZFdBdGFXMThBRjFOS0F3Z0REd3dNREFBUSJdLFstNjEsIi0iXSxbLTczLCJFaFE9Il0sWy0yNCwiW10iXSxbLTEwLCItIl0sWy0xMywiLSJdLFstMiwiMTIsZWNYRlgxLzdudHZUZGxXN0s3NlNFRUNDRUpCQVJFV3VpZzBsRUlTQmNRUlVGQlFlbWhpQ0NJU3BVcUlJalNPMUlOaUNLOXBpY2tJVDJiYko5NTVkNTc3djkzM3N6Ym5Td0pJUCJdLFstMzIsIjAiXSxbLTQxLCItIl0sWy02MiwiODAiXSxbLTQsIi0iXSxbLTUsIi0iXSxbLTQ0LCIwLDAsMCw1Il0sWy05LCIrIl0sWzEyLCJ7XCJjdHhcIjpcIndlYmdsXCIsXCJ2XCI6XCJnb29nbGUgaW5jLiAoZ29vZ2xlKVwiLFwiclwiOlwiYW5nbGUgKGdvb2dsZSwgdnVsa2FuIDEuMy4wIChzd2lmdHNoYWRlciBkZXZpY2UgKHN1Ynplcm8pICgweDAwMDBjMGRlKSksIHN3aWZ0c2hhZGVyIGRyaXZlcilcIixcInNsdlwiOlwid2ViZ2wgZ2xzbCBlcyAxLjAgKG9wZW5nbCBlcyBnbHNsIGVzIDEuMCBjaHJvbWl1bSlcIixcImd2ZXJcIjpcIndlYmdsIDEuMCAob3BlbmdsIGVzIDIuMCBjaHJvbWl1bSlcIixcImd2ZW5cIjpcIndlYmtpdFwiLFwiYmVuXCI6MTAsXCJ3Z2xcIjoxLFwiZ3JlblwiOlwid2Via2l0IHdlYmdsXCIsXCJzZWZcIjoxOTMwODIwMjc5LFwic2VjXCI6XCJcIn0iXSxbLTUwLCItIl0sWy01MSwiLSJdLFstMzMsIi0iXSxbLTU2LCJsYW5kc2NhcGUtcHJpbWFyeSJdLFstMzYsIltcIjQvM1wiLFwiNC8zXCJdIl0sWy0xNiwiMCJdLFstNDgsIltcIi1cIixcIi1cIixcIi1cIixcIi1cIixcIi1cIl0iXSxbLTQ5LCItIl0sWy0yOCwiZW4tVVMiXSxbLTI5LCItIl0sWy0zMSwiZmFsc2UiXSxbLTM0LCItIl0sWy0xNCwiLSJdLFstMzUsIlsxNzU2MTUwMjIzODQxLDddIl0sWy00MiwiODgzMzk5MDE2Il0sWy02NSwiLSJdLFstNTIsIi0iXSxbLTE1LCItIl0sWy01OSwiZGVuaWVkIl0sWy0zOCwiaSwtMSwtMSwwLDAsMCwwLDAsMCwyMTg2LC0xLDAsLCwyNTQzLDI1NDQiXSxbLTYwLCItIl0sWy0yMSwiLSJdLFstMjMsIisiXSxbLTE3LCI1NiJdLFstNDAsIjMzIl0sWy02MywiMTYiXSxbLTQ1LCI2MjAsMCwwLDAsMCw1NjIsMCwwLDY0OCw1ODMsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCJdLFstMjUsIi0iXSxbLTExLCJ7XCJ0XCI6XCJcIixcIm1cIjpbXCJkZXNjcmlwdGlvblwiXX0iXSxbLTMwLCJbXCJ2XCIsMF0iXSxbLTY4LCItIl0sWy01NCwie1wiaFwiOltcIjMyOTk3Mjg0NTJcIixcIjgyMjgyMzExOVwiLFwiXzNcIixcIjI4NzI4OTkzMjBcIl0sXCJkXCI6W10sXCJiXCI6W1wiXzBcIixcIjI2NDYwMzg4MlwiXSxcInNcIjoxfSJdLFstMSwiLSJdLFstMywiW10iXSxbLTIwLCItIl0sWy00NywiQW1lcmljYS9Mb3NfQW5nZWxlcyxlbi1VUyxsYXRuLGdyZWdvcnkiXSxbLTgsIi0iXSxbLTI3LCJbMCwxMCwwLFwiNGdcIixudWxsXSJdLFstNjYsImdlb2xvY2F0aW9uLGNodWFmdWxsdmVyc2lvbmxpc3QsY3Jvc3NvcmlnaW5pc29sYXRlZCxzY3JlZW53YWtlbG9jayxwdWJsaWNrZXljcmVkZW50aWFsc2dldCxzaGFyZWRzdG9yYWdlc2VsZWN0dXJsLGNodWFhcmNoLGNvbXB1dGVwcmVzc3VyZSxjaHByZWZlcnNyZWR1Y2VkdHJhbnNwYXJlbmN5LGRlZmVycmVkZmV0Y2gsdXNiLGNoc2F2ZWRhdGEscHVibGlja2V5Y3JlZGVudGlhbHNjcmVhdGUsc2hhcmVkc3RvcmFnZSxkZWZlcnJlZGZldGNobWluaW1hbCxydW5hZGF1Y3Rpb24sY2hkb3dubGluayxjaHVhZm9ybWZhY3RvcnMsb3RwY3JlZGVudGlhbHMscGF5bWVudCxjaHVhLGNodWFtb2RlbCxjaGVjdCxhdXRvcGxheSxjYW1lcmEscHJpdmF0ZXN0YXRldG9rZW5pc3N1YW5jZSxhY2NlbGVyb21ldGVyLGNodWFwbGF0Zm9ybXZlcnNpb24saWRsZWRldGVjdGlvbixwcml2YXRlYWdncmVnYXRpb24saW50ZXJlc3Rjb2hvcnQsY2h2aWV3cG9ydGhlaWdodCxjYXB0dXJlZHN1cmZhY2Vjb250cm9sLGxvY2FsZm9udHMsY2h1YXBsYXRmb3JtLG1pZGksY2h1YWZ1bGx2ZXJzaW9uLHhyc3BhdGlhbHRyYWNraW5nLGNsaXBib2FyZHJlYWQsZ2FtZXBhZCxkaXNwbGF5Y2FwdHVyZSxrZXlib2FyZG1hcCxqb2luYWRpbnRlcmVzdGdyb3VwLGNod2lkdGgsY2hwcmVmZXJzcmVkdWNlZG1vdGlvbixicm93c2luZ3RvcGljcyxlbmNyeXB0ZWRtZWRpYSxneXJvc2NvcGUsc2VyaWFsLGNocnR0LGNodWFtb2JpbGUsd2luZG93bWFuYWdlbWVudCx1bmxvYWQsY2hkcHIsY2hwcmVmZXJzY29sb3JzY2hlbWUsY2h1YXdvdzY0LGF0dHJpYnV0aW9ucmVwb3J0aW5nLGZ1bGxzY3JlZW4saWRlbnRpdHljcmVkZW50aWFsc2dldCxwcml2YXRlc3RhdGV0b2tlbnJlZGVtcHRpb24saGlkLGNodWFiaXRuZXNzLHN0b3JhZ2VhY2Nlc3Msc3luY3hocixjaGRldmljZW1lbW9yeSxjaHZpZXdwb3J0d2lkdGgscGljdHVyZWlucGljdHVyZSxtYWduZXRvbWV0ZXIsY2xpcGJvYXJkd3JpdGUsbWljcm9waG9uZSJdLFstNjcsIi0iXSxbImJuY2giLDE3NF0sWy0zNywiLSJdLFstMzksIltcIjIwMDMwMTA3XCIsMCxcIkdlY2tvXCIsXCJOZXRzY2FwZVwiLFwiTW96aWxsYVwiLG51bGwsbnVsbCxmYWxzZSxudWxsLGZhbHNlLG51bGwsMCxmYWxzZSxmYWxzZSxudWxsLDAsZmFsc2UsZmFsc2UsZmFsc2UsdHJ1ZV0iXSxbLTQzLCIwMDAwMDAwMTAwMDAwMDAwMDAwMTEwMTEwMDAwMTEwMTAwMDAwMTAxMSJdLFstNjQsIi0iXSxbLTcwLCItIl0sWy01NSwiMCJdLFstNzQsIjAsMCJdLFstNTgsIi0iXSxbLTE5LCJbMCwwLDAsMCwwLDAsMSwyNCwyNCxcIi1cIiw4MDAsNjAwLDgwMCw2MDAsMSwxLDEzNTAsOTQwLDAsMCwwLDAsXCItXCIsXCItXCIsMTM1MCw5NDAsbnVsbF0iXSxbLTIyLCJbXCJuXCIsXCJuXCJdIl0sWy0yNiwie1widGpoc1wiOjQyMTAwMDAwLFwidWpoc1wiOjE1MjAwMDAwLFwiamhzbFwiOjM3NjAwMDAwMDB9Il0sWy02OSwiTGludXggeDg2XzY0fEdvb2dsZSBJbmMufHw1NnwtfC0iXSxbLTUzLCIwMDEiXSxbLTcxLCJhMDExMDAxMDEwMDEwMDEwMTAwMDEwMTAwMTExMTEwMTAwMDAxMCJdLFstNzIsIkV4VT0iXSxbImRkYiIsIjAsMTEsMCwwLDAsMiwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDEsMCwwLDAsMiwwLDAsMCwwLDAsMSwxLDMsMTYsMCw0LDEsMywwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMSwwLDE1LDAsMCwxLDAsMCwwLDEsMSwwLDAsMCJdLFsiY2IiLCIwLDAsMCwwLDAsMCwwLDAsMSwyLDAsMCwxMSwwLDAsNSwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMSwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMSwwLDEsMSwwLDAsMSwwLDAsMCwwLDEsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDEsMCwwLDAsMCwwLDAsMSwwLDAsMCwwLDAsMCwwLDAsMCwyLDAsMCwwLDEsMCwwLDEiXV0%3D&dep=0&pre=0&sdd=&cri=fqAne8RIw5&pto=2606&ver=65&gac=-&mei=&ap=&fe=1&duid=1.1756150223.YVG3JTEVgf9ywIYO&suid=1.1756150223.4bvPKt14TpOsCR9g&tuid=1.1756150223.xytAvRB2DNsL7K7j&fbc=-&gtm=-&it=7%2C2191%2C60&fbcl=-&gacl=-&gacsd=-&rtic=-&rtict=-&bgc=-&spa=1&urid=0&ab=&sck=-&io=aGA2Og%3D%3D",
              "rendererStartTime": 2611.7660007476807,
              "entity": "youseasky.com",
              "priority": "Low",
              "experimentalFromMainFrame": true,
              "networkRequestTime": 2612.7010011672974,
              "networkEndTime": 2820.2570009231567,
              "resourceSize": 3689,
              "finished": true,
              "sessionTargetType": "page",
              "resourceType": "Script",
              "mimeType": "text/javascript",
              "transferSize": 1686,
              "protocol": "h2",
              "statusCode": 200
            },
            {
              "resourceType": "Script",
              "mimeType": "text/javascript",
              "transferSize": 58321,
              "priority": "High",
              "protocol": "h2",
              "finished": true,
              "url": "https://syndicatedsearch.goog/adsense/domains/caf.js?pac=2",
              "sessionTargetType": "page",
              "resourceSize": 158382,
              "networkRequestTime": 2635.2019996643066,
              "statusCode": 200,
              "entity": "syndicatedsearch.goog",
              "networkEndTime": 2652.077000617981,
              "rendererStartTime": 2634.1870002746582
            },
            {
              "resourceType": "XHR",
              "transferSize": 539,
              "experimentalFromMainFrame": true,
              "entity": "se1gym.co.uk",
              "priority": "VeryHigh",
              "rendererStartTime": 2683.4569997787476,
              "mimeType": "text/html",
              "sessionTargetType": "page",
              "protocol": "http/1.1",
              "networkRequestTime": 2684.6430006027222,
              "resourceSize": 0,
              "statusCode": 200,
              "url": "http://www.se1gym.co.uk/munin/a/tr/answercheck/yes?domain=se1gym.co.uk&caf=1&toggle=answercheck&answer=yes&uid=MTc1NjE1MDIyMy40NDU0OmU3YWMzYzM2OGJlODZkOTc1ZDY2NjM4ZWFmZTgzZTk3Y2YyYWUyODUxYWIwZTU3YzFlMWE0MDMxMDhmNjdlNGY6NjhhY2I5Y2Y2Y2JmMA%3D%3D",
              "networkEndTime": 2799.4670000076294,
              "finished": true
            },
            {
              "mimeType": "image/svg+xml",
              "networkRequestTime": 2818.8249998092651,
              "protocol": "h2",
              "priority": "Low",
              "networkEndTime": 2826.782000541687,
              "transferSize": 1070,
              "finished": true,
              "rendererStartTime": 2818.2070007324219,
              "statusCode": 200,
              "resourceSize": 391,
              "url": "https://afs.googleusercontent.com/ad_icons/standard/publisher_icon_image/search.svg?c=%23ffffff",
              "entity": "googleusercontent.com",
              "sessionTargetType": "page",
              "resourceType": "Image"
            },
            {
              "networkEndTime": 2829.689001083374,
              "sessionTargetType": "page",
              "entity": "googleusercontent.com",
              "transferSize": 973,
              "networkRequestTime": 2819.1890001296997,
              "statusCode": 200,
              "finished": true,
              "resourceSize": 200,
              "mimeType": "image/svg+xml",
              "url": "https://afs.googleusercontent.com/ad_icons/standard/publisher_icon_image/chevron.svg?c=%23ffffff",
              "rendererStartTime": 2818.4240007400513,
              "resourceType": "Image",
              "priority": "Low",
              "protocol": "h2"
            },
            {
              "url": "https://www.google.com/js/bg/Z-SsKYkj_Kr8t4L84tyvkiZZMnLnK5CX23Vh5jPe2Hs.js",
              "transferSize": 23076,
              "resourceType": "Script",
              "entity": "Other Google APIs/SDKs",
              "sessionTargetType": "page",
              "mimeType": "text/javascript",
              "statusCode": 200,
              "networkRequestTime": 2820.1310005187988,
              "priority": "Low",
              "protocol": "h2",
              "resourceSize": 58415,
              "finished": true,
              "rendererStartTime": 2819.2300004959106,
              "networkEndTime": 2826.367000579834
            },
            {
              "networkRequestTime": 2830.5210008621216,
              "experimentalFromMainFrame": true,
              "finished": true,
              "networkEndTime": 3017.7190008163452,
              "sessionTargetType": "page",
              "resourceSize": 43,
              "entity": "youseasky.com",
              "priority": "Low",
              "resourceType": "Image",
              "mimeType": "image/gif",
              "url": "https://obseu.youseasky.com/tracker/tc_imp.gif?e=37dfbd8ee84e00126fe8c630ea4588999225c24f567d43d6da1908be6245cad7bd70a976750ef80ed89373bfe70e9c20c1e53e8d56118a6d2217071a10acf9f29f671f8282d8562c6b1bfd7e21578738de61ce553401279a010456640d59c0b96f4c77be26bb25cb43e2953dee536fae13246410d85afe5aecd2948a7fe07f52a13ad2a24710d14e681f2d1586d31c64e56ad2b785ba130be20ad7bc29917f9e3e9840f85473be5266e97c56052ca4482bc9d8a5e416af3db153bb46a1352837a6d2347e25795f957df2e57d8d7829e8cfe879186a5583d5757f92902f46681b2c5214a68d2a7e7d19a4e44969effaa37fd2b944771e2bb5a5a384eb2ffc82830ff62ac50f662695b7dff6a3268ccea03ed62104c3ac9c2d4c14f5356cad914265bddfaf27dd53ae4fe6d719cb4b9e9e7ec63961918b3bca3bc5c0e2f088eee01136e46af4e7e823436cf897239aab5df402011f94085bd2998c84c0f1c927c16790d0f58e7fae24287ac4682c97859c426788b821e541e6d315d6409e3d0c0b548c6eec439cd0ad3fe0d776870ce08bdbcb7789490435bd1e5a137f433e9fec40b254f2cb892fe7d127fb9d23d989e5bc32cdbee453607584ec4c47deb0491442f8eff63ff36bdeb303b1f224a022b22d870485678bf169995e5eb0bc9874222d7c117c592f4bf3b4d228ab56a54f5c5e3be4a60d838a1267fcb8c3bbbd6edeeee6fa9afbaef2574e3dfe5b87b6596d815f6307ca61596d71f472b36b18c1ebdd7e8d61d23996ad2ecda4109e7b0b3d3d057d1080dde3da3867489c184589cedfbbb2d64e039eb3d061849b36228cc0182e68e790de5327b622855d9d19fd56fd65d8b2778ddc65b492c195e12e1dfdfc2920c72ff29fbab917826d331303956d4352b3a0418bbe52aae2dfc950a9c7f8707d554ee92fb717ee10ebd57b9c20423f403d7879e05f8e833156a72789e38473bbbd4ff80a30d316072bc5facd1818ae27e7847bb1012d014abc3b3283c2ba74d9157ac39719a1c3cfabd1068b210a7144b62e7a0cfec55b05e562f5f4c3319d87b94c4f76a06a3c1a44924642ec9bf20a51cd3733c19d8541d5c6fa921b30b031b9076350ca5231209683555381d4ffc4bdf140b478b464d725dd9d5d87beba393dee8640c298b9aed6aa809826488dfa3704d82d980b985fe7ed37ba8d898c37a08c8bbda71a6786b8a58703b308d7014d3b4c3fd89a6f678026bf10&cri=fqAne8RIw5&ts=224&cb=1756150224129",
              "statusCode": 200,
              "protocol": "h2",
              "rendererStartTime": 2829.246000289917,
              "transferSize": 249
            },
            {
              "mimeType": "text/plain",
              "networkEndTime": 3007.8650007247925,
              "priority": "VeryLow",
              "rendererStartTime": 2837.3940000534058,
              "resourceSize": 535,
              "networkRequestTime": 2837.3940000534058,
              "resourceType": "Script",
              "transferSize": -1,
              "finished": true,
              "protocol": "blob",
              "statusCode": 200,
              "sessionTargetType": "worker",
              "url": "blob:http://www.se1gym.co.uk/45bba7a7-ad83-4667-bb33-36a91e44acbc"
            },
            {
              "statusCode": 200,
              "finished": true,
              "mimeType": "application/json",
              "url": "https://ep1.adtrafficquality.google/getconfig/sodar?sv=200&tid=afs&tv=10&st=env",
              "experimentalFromMainFrame": true,
              "priority": "High",
              "rendererStartTime": 3020.9330005645752,
              "resourceType": "XHR",
              "networkRequestTime": 3021.6120004653931,
              "networkEndTime": 3029.2670001983643,
              "entity": "adtrafficquality.google",
              "protocol": "h2",
              "transferSize": 6896,
              "resourceSize": 8406,
              "sessionTargetType": "page"
            },
            {
              "finished": true,
              "transferSize": 664,
              "mimeType": "text/html",
              "resourceType": "Image",
              "url": "https://syndicatedsearch.goog/afs/gen_204?client=dp-teaminternet09_3ph&output=uds_ads_only&zx=ln713idy80hw&cd_fexp=72717108%2C73027842&aqid=z7msaPCANfHZywXK5ZegAg&psid=5837883959&pbt=ri&emsg=sodar_latency&rt=1.8999996185302734&ea=10",
              "priority": "Low",
              "sessionTargetType": "page",
              "experimentalFromMainFrame": true,
              "entity": "syndicatedsearch.goog",
              "networkEndTime": 3042.3280000686646,
              "resourceSize": 0,
              "protocol": "h2",
              "statusCode": 204,
              "rendererStartTime": 3021.7950000762939,
              "networkRequestTime": 3022.5690011978149
            },
            {
              "finished": true,
              "transferSize": 7852,
              "sessionTargetType": "page",
              "entity": "adtrafficquality.google",
              "mimeType": "text/javascript",
              "url": "https://ep2.adtrafficquality.google/sodar/sodar2.js",
              "resourceType": "Script",
              "resourceSize": 19990,
              "experimentalFromMainFrame": true,
              "priority": "Low",
              "protocol": "h2",
              "networkEndTime": 3036.1470003128052,
              "statusCode": 200,
              "networkRequestTime": 3031.9490003585815,
              "rendererStartTime": 3031.1409997940063
            },
            {
              "sessionTargetType": "page",
              "transferSize": 5732,
              "networkRequestTime": 3046.585000038147,
              "url": "https://ep2.adtrafficquality.google/sodar/sodar2/237/runner.html",
              "finished": true,
              "resourceType": "Document",
              "rendererStartTime": 3044.6000003814697,
              "resourceSize": 13159,
              "networkEndTime": 3050.7920007705688,
              "entity": "adtrafficquality.google",
              "priority": "VeryHigh",
              "protocol": "h2",
              "statusCode": 200,
              "mimeType": "text/html"
            },
            {
              "mimeType": "text/javascript",
              "priority": "Low",
              "networkEndTime": 3071.94700050354,
              "statusCode": 200,
              "rendererStartTime": 3066.7080001831055,
              "entity": "Google/Doubleclick Ads",
              "transferSize": 21934,
              "finished": true,
              "resourceType": "Script",
              "sessionTargetType": "page",
              "protocol": "h2",
              "resourceSize": 55315,
              "url": "https://pagead2.googlesyndication.com/bg/qoxIykLQHporMav0XsqS8NtTd2boZuUJaM-UYWb_7aA.js",
              "networkRequestTime": 3067.5790004730225
            },
            {
              "rendererStartTime": 3306.2180004119873,
              "resourceSize": 0,
              "priority": "Low",
              "sessionTargetType": "page",
              "statusCode": 204,
              "finished": true,
              "transferSize": 152,
              "networkRequestTime": 3306.9850006103516,
              "networkEndTime": 3308.8819999694824,
              "url": "https://ep2.adtrafficquality.google/generate_204?VP_7Ww",
              "entity": "adtrafficquality.google",
              "mimeType": "text/plain",
              "protocol": "h2",
              "resourceType": "Image"
            },
            {
              "sessionTargetType": "page",
              "statusCode": 200,
              "experimentalFromMainFrame": true,
              "resourceType": "XHR",
              "networkEndTime": 3965.2799997329712,
              "entity": "youseasky.com",
              "transferSize": 258,
              "resourceSize": 0,
              "priority": "High",
              "networkRequestTime": 3869.4790010452271,
              "protocol": "h2",
              "finished": true,
              "url": "https://obseu.youseasky.com/mon",
              "mimeType": "application/json",
              "rendererStartTime": 3868.5950002670288
            },
            {
              "mimeType": "image/",
              "sessionTargetType": "page",
              "finished": true,
              "protocol": "h2",
              "rendererStartTime": 3974.5780010223389,
              "priority": "Low",
              "networkRequestTime": 3975.9100008010864,
              "experimentalFromMainFrame": true,
              "url": "https://ep1.adtrafficquality.google/pagead/sodar?id=sodar2&v=237&t=2&li=afs_10&jk=0LmsaODgE9_r-cAP17iK0Qg&bg=!4OOl46zNAAbD0V7L49E7ADQBe5WfOBu12a6apHAunArmXJ_piUmk7r8CD2KxYXsGFaeoc05-zyQIlMHdOu4kFFakGVYHAgAAAMVSAAAAB2gBB34AE9k91IHfgjjLAz_ntdwV8U98_HgKAXGyDie6Xq-g4bXSzYBGDBdnEyINGYxSpauWSXNTZDkiTP6pMtI9lsyqmf5m35zsPLl70UOAxK2MDNsFY3V0xGbqkTLcWRgTVlLP6Tu2hyWkax6RHOqbX6mEmKzfhcaPXyez5YOmEdAn2EqtaMeOES58w9uLeqbHIz2JdsSXeKCa--qIxpl02fmqX95Gww6rbhr3Ix5PWrBA58LnM-JNYrG92XRHocbU8ldKDidpEL1mS9uu4HHSfnMhjnJTe-dSJE64ohWfoWUiF9THWX1UAEJYcw90nc2mP-DjuWHLfHiiG_Y4lQ7ybtWkMcWsk7iAaCPDjPq4AtoLKuAmTaZ0hYc9jgIDr5jMbZM_s4yqUFMCVMXKAsLYcXgbSE0-Q1Vh9cacXBY6cpnjLHonbYTfLSG74u6TukM4e_dElOTAT2lYmkRVjWDNvazSzNDuSDM5o0jQvodwtIL3eKJJdh8VldYa79Ploh7I9xvtWLYKmBzxFuGZAUNrV4mJvw2wWDbDaSZcowwlUwJGWXwEIHvRuUtzzvcpGyiAqs7x8WwZB8ttD473ZxQ49b5ZI2loa3PclTZr-kNezlZ3iD8Dh3LAU83dIulbf7gkWPelerrQtuhgtvGsixqI_N71A6F9uhq4Z08XwtdGTvvj_Dhb3IBN7SNn92ZqZnsjvN4NkDVdyM_yYW5IUXdiU6VBO8O2mfxTTqL7OVOdsAq9WrFiXDQEcIozkitPASBpXrg4FLX0R0fpuFl-iIs16vXABBp3fe4dMsjJTlULAKTRc_-S22XDhjduzdtYl-MYyXs4Bni-x5qYQ00fu5aT9dfvIMuAm2cg50vbbNFBssQaGCLpcRkvjpOF8HBMht26cBFi9otqsWQm9cdXs6zn8fXYLu3TTw42X25lxir73lPvKy6OGXEZCR3__s2oMrahZA",
              "transferSize": 382,
              "resourceType": "Image",
              "networkEndTime": 3981.6220006942749,
              "entity": "adtrafficquality.google",
              "statusCode": 204,
              "resourceSize": 0
            },
            {
              "transferSize": 664,
              "networkEndTime": 4328.2760000228882,
              "statusCode": 204,
              "entity": "syndicatedsearch.goog",
              "resourceSize": 0,
              "priority": "Low",
              "protocol": "h2",
              "finished": true,
              "resourceType": "Image",
              "url": "https://syndicatedsearch.goog/afs/gen_204?client=dp-teaminternet09_3ph&output=uds_ads_only&zx=4ouv3ygraqj9&cd_fexp=72717108%2C73027842&aqid=z7msaPCANfHZywXK5ZegAg&psid=5837883959&pbt=bs&adbx=410&adby=129&adbh=498&adbw=530&adbah=160%2C160%2C160&adbn=master-1&eawp=partner-dp-teaminternet09_3ph&errv=796426389&csala=9%7C0%7C133%7C35%7C133&lle=0&ifv=1&hpt=1",
              "networkRequestTime": 4309.7110004425049,
              "rendererStartTime": 4308.9150009155273,
              "experimentalFromMainFrame": true,
              "sessionTargetType": "page",
              "mimeType": "text/html"
            },
            {
              "transferSize": 664,
              "sessionTargetType": "page",
              "statusCode": 204,
              "entity": "syndicatedsearch.goog",
              "finished": true,
              "rendererStartTime": 4309.8699998855591,
              "mimeType": "text/html",
              "experimentalFromMainFrame": true,
              "networkEndTime": 4323.7709999084473,
              "resourceSize": 0,
              "resourceType": "Image",
              "priority": "Low",
              "url": "https://syndicatedsearch.goog/afs/gen_204?client=dp-teaminternet09_3ph&output=uds_ads_only&zx=h02t5ltnisir&cd_fexp=72717108%2C73027842&aqid=z7msaPCANfHZywXK5ZegAg&psid=5837883959&pbt=bv&adbx=410&adby=129&adbh=498&adbw=530&adbah=160%2C160%2C160&adbn=master-1&eawp=partner-dp-teaminternet09_3ph&errv=796426389&csala=9%7C0%7C133%7C35%7C133&lle=0&ifv=1&hpt=1",
              "protocol": "h2",
              "networkRequestTime": 4310.3640003204346
            },
            {
              "transferSize": 258,
              "finished": true,
              "protocol": "h2",
              "statusCode": 200,
              "resourceType": "XHR",
              "sessionTargetType": "page",
              "entity": "youseasky.com",
              "resourceSize": 0,
              "mimeType": "application/json",
              "experimentalFromMainFrame": true,
              "url": "https://obseu.youseasky.com/mon",
              "rendererStartTime": 5902.9890003204346,
              "priority": "High",
              "networkEndTime": 6102.3150005340576,
              "networkRequestTime": 5903.8100004196167
            },
            {
              "networkRequestTime": 7943.41900062561,
              "sessionTargetType": "page",
              "url": "https://obseu.youseasky.com/mon",
              "experimentalFromMainFrame": true,
              "transferSize": 258,
              "resourceType": "XHR",
              "rendererStartTime": 7942.6990003585815,
              "protocol": "h2",
              "resourceSize": 0,
              "priority": "High",
              "statusCode": 200,
              "mimeType": "application/json",
              "networkEndTime": 7995.9500007629395,
              "finished": true,
              "entity": "youseasky.com"
            }
          ],
          "debugData": {
            "type": "debugdata",
            "networkStartTimeTs": 6426906043992
          },
          "headings": [
            {
              "label": "URL",
              "valueType": "url",
              "key": "url"
            },
            {
              "valueType": "text",
              "label": "Protocol",
              "key": "protocol"
            },
            {
              "valueType": "ms",
              "granularity": 1,
              "key": "networkRequestTime",
              "label": "Network Request Time"
            },
            {
              "granularity": 1,
              "valueType": "ms",
              "label": "Network End Time",
              "key": "networkEndTime"
            },
            {
              "valueType": "bytes",
              "key": "transferSize",
              "granularity": 1,
              "displayUnit": "kb",
              "label": "Transfer Size"
            },
            {
              "displayUnit": "kb",
              "valueType": "bytes",
              "key": "resourceSize",
              "label": "Resource Size",
              "granularity": 1
            },
            {
              "key": "statusCode",
              "valueType": "text",
              "label": "Status Code"
            },
            {
              "key": "mimeType",
              "label": "MIME Type",
              "valueType": "text"
            },
            {
              "key": "resourceType",
              "label": "Resource Type",
              "valueType": "text"
            }
          ]
        }
      },
      "offscreen-images": {
        "id": "offscreen-images",
        "title": "Defer offscreen images",
        "description": "Consider lazy-loading offscreen and hidden images after all critical resources have finished loading to lower time to interactive. [Learn how to defer offscreen images](https://developer.chrome.com/docs/lighthouse/performance/offscreen-images/).",
        "score": 1,
        "scoreDisplayMode": "metricSavings",
        "metricSavings": {
          "LCP": 0,
          "FCP": 0
        },
        "details": {
          "items": [],
          "type": "opportunity",
          "debugData": {
            "metricSavings": {
              "LCP": 0,
              "FCP": 0
            },
            "type": "debugdata"
          },
          "overallSavingsBytes": 0,
          "headings": [],
          "overallSavingsMs": 0,
          "sortedBy": [
            "wastedBytes"
          ]
        },
        "warnings": [],
        "numericValue": 0,
        "numericUnit": "millisecond"
      },
      "duplicate-id-aria": {
        "id": "duplicate-id-aria",
        "title": "ARIA IDs are unique",
        "description": "The value of an ARIA ID must be unique to prevent other instances from being overlooked by assistive technologies. [Learn how to fix duplicate ARIA IDs](https://dequeuniversity.com/rules/axe/4.10/duplicate-id-aria).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "font-size": {
        "id": "font-size",
        "title": "Document uses legible font sizes",
        "description": "Font sizes less than 12px are too small to be legible and require mobile visitors to “pinch to zoom” in order to read. Strive to have >60% of page text ≥12px. [Learn more about legible font sizes](https://developer.chrome.com/docs/lighthouse/seo/font-size/).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "landmark-one-main": {
        "id": "landmark-one-main",
        "title": "Document has a main landmark.",
        "description": "One main landmark helps screen reader users navigate a web page. [Learn more about landmarks](https://dequeuniversity.com/rules/axe/4.10/landmark-one-main).",
        "score": 1,
        "scoreDisplayMode": "informative",
        "details": {
          "items": [
            {
              "node": {
                "nodeLabel": "html",
                "lhId": "1-4-HTML",
                "snippet": "<html data-adblockkey=\"MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBALquDFETXRn0Hr05fUP7EJT77xYnPmRbpMy4vk8KYi…\" xmlns=\"http://www.w3.org/1999/xhtml\" lang=\"en\">",
                "selector": "html",
                "boundingRect": {
                  "right": 1350,
                  "width": 1350,
                  "height": 814,
                  "left": 0,
                  "top": 0,
                  "bottom": 814
                },
                "path": "1,HTML",
                "type": "node",
                "explanation": "Fix all of the following:\n  Document does not have a main landmark"
              }
            }
          ],
          "headings": [
            {
              "key": "node",
              "valueType": "node",
              "subItemsHeading": {
                "valueType": "node",
                "key": "relatedNode"
              },
              "label": "Failing Elements"
            }
          ],
          "debugData": {
            "type": "debugdata",
            "tags": [
              "cat.semantics",
              "best-practice"
            ],
            "impact": "moderate"
          },
          "type": "table"
        }
      },
      "html-lang-valid": {
        "id": "html-lang-valid",
        "title": "`<html>` element has a valid value for its `[lang]` attribute",
        "description": "Specifying a valid [BCP 47 language](https://www.w3.org/International/questions/qa-choosing-language-tags#question) helps screen readers announce text properly. [Learn how to use the `lang` attribute](https://dequeuniversity.com/rules/axe/4.10/html-lang-valid).",
        "score": 1,
        "scoreDisplayMode": "binary",
        "details": {
          "type": "table",
          "items": [],
          "headings": [
            {
              "subItemsHeading": {
                "key": "relatedNode",
                "valueType": "node"
              },
              "label": "Failing Elements",
              "key": "node",
              "valueType": "node"
            }
          ]
        }
      },
      "geolocation-on-start": {
        "id": "geolocation-on-start",
        "title": "Avoids requesting the geolocation permission on page load",
        "description": "Users are mistrustful of or confused by sites that request their location without context. Consider tying the request to a user action instead. [Learn more about the geolocation permission](https://developer.chrome.com/docs/lighthouse/best-practices/geolocation-on-start/).",
        "score": 1,
        "scoreDisplayMode": "binary",
        "details": {
          "type": "table",
          "items": [],
          "headings": [
            {
              "label": "Source",
              "key": "source",
              "valueType": "source-location"
            }
          ]
        }
      },
      "html-has-lang": {
        "id": "html-has-lang",
        "title": "`<html>` element has a `[lang]` attribute",
        "description": "If a page doesn't specify a `lang` attribute, a screen reader assumes that the page is in the default language that the user chose when setting up the screen reader. If the page isn't actually in the default language, then the screen reader might not announce the page's text correctly. [Learn more about the `lang` attribute](https://dequeuniversity.com/rules/axe/4.10/html-has-lang).",
        "score": 1,
        "scoreDisplayMode": "binary",
        "details": {
          "headings": [
            {
              "valueType": "node",
              "key": "node",
              "subItemsHeading": {
                "key": "relatedNode",
                "valueType": "node"
              },
              "label": "Failing Elements"
            }
          ],
          "items": [],
          "type": "table"
        }
      },
      "forced-reflow-insight": {
        "id": "forced-reflow-insight",
        "title": "Forced reflow",
        "description": "A forced reflow occurs when JavaScript queries geometric properties (such as offsetWidth) after styles have been invalidated by a change to the DOM state. This can result in poor performance. Learn more about [forced reflows](https://developers.google.com/web/fundamentals/performance/rendering/avoid-large-complex-layouts-and-layout-thrashing#avoid-forced-synchronous-layouts) and possible mitigations.",
        "score": 1,
        "scoreDisplayMode": "numeric",
        "details": {
          "items": [
            {
              "items": [],
              "type": "table",
              "headings": [
                {
                  "key": "source",
                  "valueType": "source-location",
                  "label": "Source"
                },
                {
                  "granularity": 1,
                  "valueType": "ms",
                  "label": "Total reflow time",
                  "key": "reflowTime"
                }
              ]
            }
          ],
          "type": "list"
        }
      },
      "link-in-text-block": {
        "id": "link-in-text-block",
        "title": "Links are distinguishable without relying on color.",
        "description": "Low-contrast text is difficult or impossible for many users to read. Link text that is discernible improves the experience for users with low vision. [Learn how to make links distinguishable](https://dequeuniversity.com/rules/axe/4.10/link-in-text-block).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "unminified-javascript": {
        "id": "unminified-javascript",
        "title": "Minify JavaScript",
        "description": "Minifying JavaScript files can reduce payload sizes and script parse time. [Learn how to minify JavaScript](https://developer.chrome.com/docs/lighthouse/performance/unminified-javascript/).",
        "score": 1,
        "scoreDisplayMode": "metricSavings",
        "metricSavings": {
          "LCP": 0,
          "FCP": 0
        },
        "details": {
          "overallSavingsBytes": 0,
          "items": [],
          "overallSavingsMs": 0,
          "headings": [],
          "debugData": {
            "metricSavings": {
              "LCP": 0,
              "FCP": 0
            },
            "type": "debugdata"
          },
          "sortedBy": [
            "wastedBytes"
          ],
          "type": "opportunity"
        },
        "warnings": [],
        "numericValue": 0,
        "numericUnit": "millisecond"
      },
      "uses-responsive-images": {
        "id": "uses-responsive-images",
        "title": "Properly size images",
        "description": "Serve images that are appropriately-sized to save cellular data and improve load time. [Learn how to size images](https://developer.chrome.com/docs/lighthouse/performance/uses-responsive-images/).",
        "score": 1,
        "scoreDisplayMode": "metricSavings",
        "metricSavings": {
          "LCP": 0,
          "FCP": 0
        },
        "details": {
          "debugData": {
            "metricSavings": {
              "FCP": 0,
              "LCP": 0
            },
            "type": "debugdata"
          },
          "sortedBy": [
            "wastedBytes"
          ],
          "type": "opportunity",
          "overallSavingsBytes": 0,
          "headings": [],
          "items": [],
          "overallSavingsMs": 0
        },
        "numericValue": 0,
        "numericUnit": "millisecond"
      },
      "deprecations": {
        "id": "deprecations",
        "title": "Uses deprecated APIs",
        "description": "Deprecated APIs will eventually be removed from the browser. [Learn more about deprecated APIs](https://developer.chrome.com/docs/lighthouse/best-practices/deprecations/).",
        "score": 0,
        "scoreDisplayMode": "binary",
        "displayValue": "1 warning found",
        "details": {
          "headings": [
            {
              "valueType": "text",
              "label": "Deprecation / Warning",
              "key": "value"
            },
            {
              "valueType": "source-location",
              "label": "Source",
              "key": "source"
            }
          ],
          "type": "table",
          "items": [
            {
              "value": "Synchronous XMLHttpRequest on the main thread is deprecated because of its detrimental effects to the end user's experience. For more help, check https://xhr.spec.whatwg.org/.",
              "source": {
                "url": "http://www.se1gym.co.uk/",
                "type": "source-location",
                "line": 341,
                "urlProvider": "network",
                "column": 5778
              }
            }
          ]
        }
      },
      "cumulative-layout-shift": {
        "id": "cumulative-layout-shift",
        "title": "Cumulative Layout Shift",
        "description": "Cumulative Layout Shift measures the movement of visible elements within the viewport. [Learn more about the Cumulative Layout Shift metric](https://web.dev/articles/cls).",
        "score": 1,
        "scoreDisplayMode": "numeric",
        "displayValue": "0.001",
        "details": {
          "type": "debugdata",
          "items": [
            {
              "newEngineResultDiffered": false,
              "newEngineResult": {
                "cumulativeLayoutShiftMainFrame": 0.0014474920852919878,
                "cumulativeLayoutShift": 0.0014474920852919878
              },
              "cumulativeLayoutShiftMainFrame": 0.0014474920852919878
            }
          ]
        },
        "numericValue": 0.0014474920852919878,
        "numericUnit": "unitless"
      },
      "legacy-javascript": {
        "id": "legacy-javascript",
        "title": "Avoid serving legacy JavaScript to modern browsers",
        "description": "Polyfills and transforms enable legacy browsers to use new JavaScript features. However, many aren't necessary for modern browsers. Consider modifying your JavaScript build process to not transpile [Baseline](https://web.dev/baseline) features, unless you know you must support legacy browsers. [Learn why most sites can deploy ES6+ code without transpiling](https://philipwalton.com/articles/the-state-of-es5-on-the-web/)",
        "score": 0.5,
        "scoreDisplayMode": "metricSavings",
        "metricSavings": {
          "LCP": 0,
          "FCP": 0
        },
        "details": {
          "sortedBy": [
            "wastedBytes"
          ],
          "headings": [
            {
              "key": "url",
              "valueType": "url",
              "label": "URL",
              "subItemsHeading": {
                "valueType": "source-location",
                "key": "location"
              }
            },
            {
              "subItemsHeading": {
                "key": "signal"
              },
              "key": null,
              "valueType": "code"
            },
            {
              "key": "wastedBytes",
              "label": "Est Savings",
              "valueType": "bytes"
            }
          ],
          "overallSavingsMs": 0,
          "type": "opportunity",
          "debugData": {
            "metricSavings": {
              "FCP": 0,
              "LCP": 0
            },
            "type": "debugdata"
          },
          "overallSavingsBytes": 0,
          "items": [
            {
              "url": "http://www.google.com/adsense/domains/caf.js?abp=1&adsdeli=true",
              "wastedBytes": 0,
              "totalBytes": 0,
              "subItems": {
                "type": "subitems",
                "items": [
                  {
                    "location": {
                      "url": "http://www.google.com/adsense/domains/caf.js?abp=1&adsdeli=true",
                      "line": 7,
                      "column": 175,
                      "type": "source-location",
                      "urlProvider": "network"
                    },
                    "signal": "@babel/plugin-transform-regenerator"
                  }
                ]
              }
            },
            {
              "url": "https://syndicatedsearch.goog/adsense/domains/caf.js?pac=2",
              "subItems": {
                "type": "subitems",
                "items": [
                  {
                    "location": {
                      "url": "https://syndicatedsearch.goog/adsense/domains/caf.js?pac=2",
                      "urlProvider": "network",
                      "type": "source-location",
                      "line": 7,
                      "column": 175
                    },
                    "signal": "@babel/plugin-transform-regenerator"
                  }
                ]
              },
              "wastedBytes": 0,
              "totalBytes": 0
            },
            {
              "subItems": {
                "type": "subitems",
                "items": [
                  {
                    "location": {
                      "url": "https://ep2.adtrafficquality.google/sodar/sodar2.js",
                      "type": "source-location",
                      "urlProvider": "network",
                      "column": 42,
                      "line": 8
                    },
                    "signal": "@babel/plugin-transform-regenerator"
                  }
                ]
              },
              "url": "https://ep2.adtrafficquality.google/sodar/sodar2.js",
              "wastedBytes": 0,
              "totalBytes": 0
            },
            {
              "wastedBytes": 0,
              "url": "https://ep2.adtrafficquality.google/sodar/sodar2/237/runner.html",
              "subItems": {
                "type": "subitems",
                "items": [
                  {
                    "signal": "@babel/plugin-transform-regenerator",
                    "location": {
                      "urlProvider": "network",
                      "column": 42,
                      "line": 8,
                      "type": "source-location",
                      "url": "https://ep2.adtrafficquality.google/sodar/sodar2/237/runner.html"
                    }
                  }
                ]
              },
              "totalBytes": 0
            }
          ]
        },
        "warnings": [],
        "numericValue": 0,
        "numericUnit": "millisecond"
      },
      "offscreen-content-hidden": {
        "id": "offscreen-content-hidden",
        "title": "Offscreen content is hidden from assistive technology",
        "description": "Offscreen content is hidden with display: none or aria-hidden=true. [Learn how to properly hide offscreen content](https://developer.chrome.com/docs/lighthouse/accessibility/offscreen-content-hidden/).",
        "score": null,
        "scoreDisplayMode": "manual"
      },
      "origin-isolation": {
        "id": "origin-isolation",
        "title": "Ensure proper origin isolation with COOP",
        "description": "The Cross-Origin-Opener-Policy (COOP) can be used to isolate the top-level window from other documents such as pop-ups. [Learn more about deploying the COOP header.](https://web.dev/articles/why-coop-coep#coop)",
        "score": 1,
        "scoreDisplayMode": "informative",
        "details": {
          "headings": [
            {
              "label": "Description",
              "key": "description",
              "subItemsHeading": {
                "key": "description"
              },
              "valueType": "text"
            },
            {
              "subItemsHeading": {
                "key": "directive"
              },
              "label": "Directive",
              "valueType": "code",
              "key": "directive"
            },
            {
              "subItemsHeading": {
                "key": "severity"
              },
              "valueType": "text",
              "label": "Severity",
              "key": "severity"
            }
          ],
          "type": "table",
          "items": [
            {
              "severity": "High",
              "description": "No COOP header found"
            }
          ]
        }
      },
      "aria-hidden-focus": {
        "id": "aria-hidden-focus",
        "title": "`[aria-hidden=\"true\"]` elements do not contain focusable descendents",
        "description": "Focusable descendents within an `[aria-hidden=\"true\"]` element prevent those interactive elements from being available to users of assistive technologies like screen readers. [Learn how `aria-hidden` affects focusable elements](https://dequeuniversity.com/rules/axe/4.10/aria-hidden-focus).",
        "score": 1,
        "scoreDisplayMode": "binary",
        "details": {
          "type": "table",
          "headings": [
            {
              "label": "Failing Elements",
              "key": "node",
              "valueType": "node",
              "subItemsHeading": {
                "valueType": "node",
                "key": "relatedNode"
              }
            }
          ],
          "items": []
        }
      },
      "inp-breakdown-insight": {
        "id": "inp-breakdown-insight",
        "title": "INP breakdown",
        "description": "Start investigating with the longest subpart. [Delays can be minimized](https://web.dev/articles/optimize-inp#optimize_interactions). To reduce processing duration, [optimize the main-thread costs](https://web.dev/articles/optimize-long-tasks), often JS.",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "server-response-time": {
        "id": "server-response-time",
        "title": "Initial server response time was short",
        "description": "Keep the server response time for the main document short because all other requests depend on it. [Learn more about the Time to First Byte metric](https://developer.chrome.com/docs/lighthouse/performance/time-to-first-byte/).",
        "score": 1,
        "scoreDisplayMode": "metricSavings",
        "displayValue": "Root document took 100 ms",
        "metricSavings": {
          "LCP": 0,
          "FCP": 0
        },
        "details": {
          "headings": [
            {
              "valueType": "url",
              "key": "url",
              "label": "URL"
            },
            {
              "valueType": "timespanMs",
              "key": "responseTime",
              "label": "Time Spent"
            }
          ],
          "overallSavingsMs": 0,
          "items": [
            {
              "url": "http://www.se1gym.co.uk/",
              "responseTime": 97
            }
          ],
          "type": "opportunity"
        },
        "numericValue": 97,
        "numericUnit": "millisecond"
      },
      "aria-tooltip-name": {
        "id": "aria-tooltip-name",
        "title": "ARIA `tooltip` elements have accessible names",
        "description": "When a tooltip element doesn't have an accessible name, screen readers announce it with a generic name, making it unusable for users who rely on screen readers. [Learn how to name `tooltip` elements](https://dequeuniversity.com/rules/axe/4.10/aria-tooltip-name).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "aria-allowed-attr": {
        "id": "aria-allowed-attr",
        "title": "`[aria-*]` attributes match their roles",
        "description": "Each ARIA `role` supports a specific subset of `aria-*` attributes. Mismatching these invalidates the `aria-*` attributes. [Learn how to match ARIA attributes to their roles](https://dequeuniversity.com/rules/axe/4.10/aria-allowed-attr).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "select-name": {
        "id": "select-name",
        "title": "Select elements have associated label elements.",
        "description": "Form elements without effective labels can create frustrating experiences for screen reader users. [Learn more about the `select` element](https://dequeuniversity.com/rules/axe/4.10/select-name).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "render-blocking-insight": {
        "id": "render-blocking-insight",
        "title": "Render blocking requests",
        "description": "Requests are blocking the page's initial render, which may delay LCP. [Deferring or inlining](https://web.dev/learn/performance/understanding-the-critical-path#render-blocking_resources) can move these network requests out of the critical path.",
        "score": null,
        "scoreDisplayMode": "notApplicable",
        "details": {
          "headings": [
            {
              "valueType": "url",
              "key": "url",
              "label": "URL"
            },
            {
              "label": "Transfer Size",
              "valueType": "bytes",
              "key": "totalBytes"
            },
            {
              "key": "wastedMs",
              "valueType": "timespanMs",
              "label": "Duration"
            }
          ],
          "items": [],
          "type": "table"
        }
      },
      "render-blocking-resources": {
        "id": "render-blocking-resources",
        "title": "Eliminate render-blocking resources",
        "description": "Resources are blocking the first paint of your page. Consider delivering critical JS/CSS inline and deferring all non-critical JS/styles. [Learn how to eliminate render-blocking resources](https://developer.chrome.com/docs/lighthouse/performance/render-blocking-resources/).",
        "score": 1,
        "scoreDisplayMode": "metricSavings",
        "metricSavings": {
          "LCP": 0,
          "FCP": 0
        },
        "details": {
          "type": "opportunity",
          "headings": [],
          "overallSavingsMs": 0,
          "items": []
        },
        "numericValue": 0,
        "numericUnit": "millisecond"
      },
      "charset": {
        "id": "charset",
        "title": "Properly defines charset",
        "description": "A character encoding declaration is required. It can be done with a `<meta>` tag in the first 1024 bytes of the HTML or in the Content-Type HTTP response header. [Learn more about declaring the character encoding](https://developer.chrome.com/docs/lighthouse/best-practices/charset/).",
        "score": 1,
        "scoreDisplayMode": "binary"
      },
      "definition-list": {
        "id": "definition-list",
        "title": "`<dl>`'s contain only properly-ordered `<dt>` and `<dd>` groups, `<script>`, `<template>` or `<div>` elements.",
        "description": "When definition lists are not properly marked up, screen readers may produce confusing or inaccurate output. [Learn how to structure definition lists correctly](https://dequeuniversity.com/rules/axe/4.10/definition-list).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "image-alt": {
        "id": "image-alt",
        "title": "Image elements have `[alt]` attributes",
        "description": "Informative elements should aim for short, descriptive alternate text. Decorative elements can be ignored with an empty alt attribute. [Learn more about the `alt` attribute](https://dequeuniversity.com/rules/axe/4.10/image-alt).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "crawlable-anchors": {
        "id": "crawlable-anchors",
        "title": "Links are not crawlable",
        "description": "Search engines may use `href` attributes on links to crawl websites. Ensure that the `href` attribute of anchor elements links to an appropriate destination, so more pages of the site can be discovered. [Learn how to make links crawlable](https://support.google.com/webmasters/answer/9112205)",
        "score": 0,
        "scoreDisplayMode": "binary",
        "details": {
          "headings": [
            {
              "key": "node",
              "label": "Uncrawlable Link",
              "valueType": "node"
            }
          ],
          "items": [
            {
              "node": {
                "nodeLabel": "Privacy Policy",
                "lhId": "1-2-A",
                "type": "node",
                "selector": "body#afd > div.wrapper1 > div.footer > a.privacy-policy",
                "boundingRect": {
                  "bottom": 721,
                  "left": 635,
                  "height": 15,
                  "right": 715,
                  "width": 80,
                  "top": 706
                },
                "snippet": "<a href=\"javascript:void(0);\" onclick=\"window.open('/privacy.html', 'privacy-policy', 'width=890,height=330,left=…\" class=\"privacy-policy\">",
                "path": "1,HTML,1,BODY,2,DIV,4,DIV,3,A"
              }
            }
          ],
          "type": "table"
        }
      },
      "custom-controls-labels": {
        "id": "custom-controls-labels",
        "title": "Custom controls have associated labels",
        "description": "Custom interactive controls have associated labels, provided by aria-label or aria-labelledby. [Learn more about custom controls and labels](https://developer.chrome.com/docs/lighthouse/accessibility/custom-controls-labels/).",
        "score": null,
        "scoreDisplayMode": "manual"
      },
      "aria-hidden-body": {
        "id": "aria-hidden-body",
        "title": "`[aria-hidden=\"true\"]` is not present on the document `<body>`",
        "description": "Assistive technologies, like screen readers, work inconsistently when `aria-hidden=\"true\"` is set on the document `<body>`. [Learn how `aria-hidden` affects the document body](https://dequeuniversity.com/rules/axe/4.10/aria-hidden-body).",
        "score": 1,
        "scoreDisplayMode": "binary",
        "details": {
          "type": "table",
          "headings": [
            {
              "subItemsHeading": {
                "valueType": "node",
                "key": "relatedNode"
              },
              "label": "Failing Elements",
              "valueType": "node",
              "key": "node"
            }
          ],
          "items": []
        }
      },
      "uses-passive-event-listeners": {
        "id": "uses-passive-event-listeners",
        "title": "Uses passive listeners to improve scrolling performance",
        "description": "Consider marking your touch and wheel event listeners as `passive` to improve your page's scroll performance. [Learn more about adopting passive event listeners](https://developer.chrome.com/docs/lighthouse/best-practices/uses-passive-event-listeners/).",
        "score": 1,
        "scoreDisplayMode": "metricSavings",
        "details": {
          "items": [],
          "type": "table",
          "headings": [
            {
              "key": "source",
              "valueType": "source-location",
              "label": "Source"
            }
          ]
        }
      },
      "diagnostics": {
        "id": "diagnostics",
        "title": "Diagnostics",
        "description": "Collection of useful page vitals.",
        "score": 1,
        "scoreDisplayMode": "informative",
        "details": {
          "items": [
            {
              "numStylesheets": 0,
              "numScripts": 9,
              "mainDocumentTransferSize": 7768,
              "numTasksOver10ms": 18,
              "numTasksOver50ms": 3,
              "rtt": 0.00093254962941952482,
              "maxServerLatency": 8,
              "numTasksOver25ms": 7,
              "maxRtt": 3.4199700000000006,
              "throughput": 12975503.354693329,
              "totalTaskTime": 1122.381999999998,
              "numTasksOver500ms": 0,
              "numTasks": 2019,
              "numTasksOver100ms": 3,
              "numRequests": 29,
              "numFonts": 1,
              "totalByteWeight": 279275
            }
          ],
          "type": "debugdata"
        }
      },
      "heading-order": {
        "id": "heading-order",
        "title": "Heading elements appear in a sequentially-descending order",
        "description": "Properly ordered headings that do not skip levels convey the semantic structure of the page, making it easier to navigate and understand when using assistive technologies. [Learn more about heading order](https://dequeuniversity.com/rules/axe/4.10/heading-order).",
        "score": 1,
        "scoreDisplayMode": "binary",
        "details": {
          "items": [],
          "headings": [
            {
              "subItemsHeading": {
                "valueType": "node",
                "key": "relatedNode"
              },
              "key": "node",
              "valueType": "node",
              "label": "Failing Elements"
            }
          ],
          "type": "table"
        }
      },
      "button-name": {
        "id": "button-name",
        "title": "Buttons have an accessible name",
        "description": "When a button doesn't have an accessible name, screen readers announce it as \"button\", making it unusable for users who rely on screen readers. [Learn how to make buttons more accessible](https://dequeuniversity.com/rules/axe/4.10/button-name).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "screenshot-thumbnails": {
        "id": "screenshot-thumbnails",
        "title": "Screenshot Thumbnails",
        "description": "This is what the load of your site looked like.",
        "score": 1,
        "scoreDisplayMode": "informative",
        "details": {
          "scale": 3007,
          "items": [
            {
              "data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEABALDA4MChAODQ4SERATGCgaGBYWGDEjJR0oOjM9PDkzODdASFxOQERXRTc4UG1RV19iZ2hnPk1xeXBkeFxlZ2MBERISGBUYLxoaL2NCOEJjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY//AABEIAVwB9AMBEQACEQEDEQH/xAGiAAABBQEBAQEBAQAAAAAAAAAAAQIDBAUGBwgJCgsQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+gEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoLEQACAQIEBAMEBwUEBAABAncAAQIDEQQFITEGEkFRB2FxEyIygQgUQpGhscEJIzNS8BVictEKFiQ04SXxFxgZGiYnKCkqNTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqCg4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2dri4+Tl5ufo6ery8/T19vf4+fr/2gAMAwEAAhEDEQA/APQKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoA//9k=",
              "timing": 376,
              "timestamp": 6426906419730
            },
            {
              "timing": 752,
              "data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEABALDA4MChAODQ4SERATGCgaGBYWGDEjJR0oOjM9PDkzODdASFxOQERXRTc4UG1RV19iZ2hnPk1xeXBkeFxlZ2MBERISGBUYLxoaL2NCOEJjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY//AABEIAVwB9AMBEQACEQEDEQH/xAGiAAABBQEBAQEBAQAAAAAAAAAAAQIDBAUGBwgJCgsQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+gEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoLEQACAQIEBAMEBwUEBAABAncAAQIDEQQFITEGEkFRB2FxEyIygQgUQpGhscEJIzNS8BVictEKFiQ04SXxFxgZGiYnKCkqNTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqCg4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2dri4+Tl5ufo6ery8/T19vf4+fr/2gAMAwEAAhEDEQA/APQKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoA//9k=",
              "timestamp": 6426906795605
            },
            {
              "timestamp": 6426907171480,
              "timing": 1128,
              "data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEABALDA4MChAODQ4SERATGCgaGBYWGDEjJR0oOjM9PDkzODdASFxOQERXRTc4UG1RV19iZ2hnPk1xeXBkeFxlZ2MBERISGBUYLxoaL2NCOEJjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY//AABEIAVwB9AMBEQACEQEDEQH/xAGiAAABBQEBAQEBAQAAAAAAAAAAAQIDBAUGBwgJCgsQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+gEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoLEQACAQIEBAMEBwUEBAABAncAAQIDEQQFITEGEkFRB2FxEyIygQgUQpGhscEJIzNS8BVictEKFiQ04SXxFxgZGiYnKCkqNTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqCg4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2dri4+Tl5ufo6ery8/T19vf4+fr/2gAMAwEAAhEDEQA/APQKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoA//9k="
            },
            {
              "data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEABALDA4MChAODQ4SERATGCgaGBYWGDEjJR0oOjM9PDkzODdASFxOQERXRTc4UG1RV19iZ2hnPk1xeXBkeFxlZ2MBERISGBUYLxoaL2NCOEJjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY//AABEIAVwB9AMBEQACEQEDEQH/xAGiAAABBQEBAQEBAQAAAAAAAAAAAQIDBAUGBwgJCgsQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+gEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoLEQACAQIEBAMEBwUEBAABAncAAQIDEQQFITEGEkFRB2FxEyIygQgUQpGhscEJIzNS8BVictEKFiQ04SXxFxgZGiYnKCkqNTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqCg4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2dri4+Tl5ufo6ery8/T19vf4+fr/2gAMAwEAAhEDEQA/APQKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoA//9k=",
              "timestamp": 6426907547355,
              "timing": 1504
            },
            {
              "data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEABALDA4MChAODQ4SERATGCgaGBYWGDEjJR0oOjM9PDkzODdASFxOQERXRTc4UG1RV19iZ2hnPk1xeXBkeFxlZ2MBERISGBUYLxoaL2NCOEJjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY//AABEIAVwB9AMBEQACEQEDEQH/xAGiAAABBQEBAQEBAQAAAAAAAAAAAQIDBAUGBwgJCgsQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+gEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoLEQACAQIEBAMEBwUEBAABAncAAQIDEQQFITEGEkFRB2FxEyIygQgUQpGhscEJIzNS8BVictEKFiQ04SXxFxgZGiYnKCkqNTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqCg4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2dri4+Tl5ufo6ery8/T19vf4+fr/2gAMAwEAAhEDEQA/APQKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoA//9k=",
              "timing": 1879,
              "timestamp": 6426907923230
            },
            {
              "timing": 2255,
              "timestamp": 6426908299105,
              "data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEABALDA4MChAODQ4SERATGCgaGBYWGDEjJR0oOjM9PDkzODdASFxOQERXRTc4UG1RV19iZ2hnPk1xeXBkeFxlZ2MBERISGBUYLxoaL2NCOEJjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY//AABEIAVwB9AMBEQACEQEDEQH/xAGiAAABBQEBAQEBAQAAAAAAAAAAAQIDBAUGBwgJCgsQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+gEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoLEQACAQIEBAMEBwUEBAABAncAAQIDEQQFITEGEkFRB2FxEyIygQgUQpGhscEJIzNS8BVictEKFiQ04SXxFxgZGiYnKCkqNTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqCg4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2dri4+Tl5ufo6ery8/T19vf4+fr/2gAMAwEAAhEDEQA/APQKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoA//9k="
            },
            {
              "data": "data:image/jpeg;base64,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",
              "timestamp": 6426908674980,
              "timing": 2631
            },
            {
              "timestamp": 6426909050855,
              "timing": 3007,
              "data": "data:image/jpeg;base64,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"
            }
          ],
          "type": "filmstrip"
        }
      },
      "viewport": {
        "id": "viewport",
        "title": "Has a `<meta name=\"viewport\">` tag with `width` or `initial-scale`",
        "description": "A `<meta name=\"viewport\">` not only optimizes your app for mobile screen sizes, but also prevents [a 300 millisecond delay to user input](https://developer.chrome.com/blog/300ms-tap-delay-gone-away/). [Learn more about using the viewport meta tag](https://developer.chrome.com/docs/lighthouse/pwa/viewport/).",
        "score": 1,
        "scoreDisplayMode": "metricSavings",
        "metricSavings": {
          "INP": 0
        },
        "details": {
          "viewportContent": "width=device-width, initial-scale=1, shrink-to-fit=no",
          "type": "debugdata"
        },
        "warnings": []
      },
      "largest-contentful-paint": {
        "id": "largest-contentful-paint",
        "title": "Largest Contentful Paint",
        "description": "Largest Contentful Paint marks the time at which the largest text or image is painted. [Learn more about the Largest Contentful Paint metric](https://developer.chrome.com/docs/lighthouse/performance/lighthouse-largest-contentful-paint/)",
        "score": 1,
        "scoreDisplayMode": "numeric",
        "displayValue": "0.5 s",
        "numericValue": 512.83807490074116,
        "numericUnit": "millisecond"
      },
      "meta-description": {
        "id": "meta-description",
        "title": "Document has a meta description",
        "description": "Meta descriptions may be included in search results to concisely summarize page content. [Learn more about the meta description](https://developer.chrome.com/docs/lighthouse/seo/meta-description/).",
        "score": 1,
        "scoreDisplayMode": "binary"
      },
      "visual-order-follows-dom": {
        "id": "visual-order-follows-dom",
        "title": "Visual order on the page follows DOM order",
        "description": "DOM order matches the visual order, improving navigation for assistive technology. [Learn more about DOM and visual ordering](https://developer.chrome.com/docs/lighthouse/accessibility/visual-order-follows-dom/).",
        "score": null,
        "scoreDisplayMode": "manual"
      },
      "target-size": {
        "id": "target-size",
        "title": "Touch targets have sufficient size and spacing.",
        "description": "Touch targets with sufficient size and spacing help users who may have difficulty targeting small controls to activate the targets. [Learn more about touch targets](https://dequeuniversity.com/rules/axe/4.10/target-size).",
        "score": 1,
        "scoreDisplayMode": "binary",
        "details": {
          "type": "table",
          "items": [],
          "headings": [
            {
              "subItemsHeading": {
                "key": "relatedNode",
                "valueType": "node"
              },
              "label": "Failing Elements",
              "key": "node",
              "valueType": "node"
            }
          ]
        }
      },
      "modern-image-formats": {
        "id": "modern-image-formats",
        "title": "Serve images in next-gen formats",
        "description": "Image formats like WebP and AVIF often provide better compression than PNG or JPEG, which means faster downloads and less data consumption. [Learn more about modern image formats](https://developer.chrome.com/docs/lighthouse/performance/uses-webp-images/).",
        "score": 1,
        "scoreDisplayMode": "metricSavings",
        "metricSavings": {
          "LCP": 0,
          "FCP": 0
        },
        "details": {
          "sortedBy": [
            "wastedBytes"
          ],
          "overallSavingsBytes": 0,
          "debugData": {
            "type": "debugdata",
            "metricSavings": {
              "FCP": 0,
              "LCP": 0
            }
          },
          "overallSavingsMs": 0,
          "items": [],
          "headings": [],
          "type": "opportunity"
        },
        "warnings": [],
        "numericValue": 0,
        "numericUnit": "millisecond"
      },
      "network-server-latency": {
        "id": "network-server-latency",
        "title": "Server Backend Latencies",
        "description": "Server latencies can impact web performance. If the server latency of an origin is high, it's an indication the server is overloaded or has poor backend performance. [Learn more about server response time](https://hpbn.co/primer-on-web-performance/#analyzing-the-resource-waterfall).",
        "score": 1,
        "scoreDisplayMode": "informative",
        "displayValue": "10 ms",
        "details": {
          "headings": [
            {
              "valueType": "text",
              "label": "URL",
              "key": "origin"
            },
            {
              "label": "Time Spent",
              "key": "serverResponseTime",
              "granularity": 1,
              "valueType": "ms"
            }
          ],
          "items": [
            {
              "origin": "http://www.google.com",
              "serverResponseTime": 8
            },
            {
              "serverResponseTime": 4,
              "origin": "https://euob.youseasky.com"
            },
            {
              "serverResponseTime": 2,
              "origin": "https://www.google.com"
            },
            {
              "serverResponseTime": 2,
              "origin": "https://pagead2.googlesyndication.com"
            },
            {
              "serverResponseTime": 1.5,
              "origin": "https://ep2.adtrafficquality.google"
            },
            {
              "serverResponseTime": 1,
              "origin": "http://www.se1gym.co.uk"
            },
            {
              "serverResponseTime": 1,
              "origin": "http://d38psrni17bvxu.cloudfront.net"
            },
            {
              "serverResponseTime": 1,
              "origin": "https://syndicatedsearch.goog"
            },
            {
              "serverResponseTime": 1,
              "origin": "https://afs.googleusercontent.com"
            },
            {
              "origin": "https://ep1.adtrafficquality.google",
              "serverResponseTime": 1
            },
            {
              "serverResponseTime": 0,
              "origin": "https://partner.googleadservices.com"
            },
            {
              "origin": "https://obseu.youseasky.com",
              "serverResponseTime": 0
            }
          ],
          "sortedBy": [
            "serverResponseTime"
          ],
          "type": "table"
        },
        "numericValue": 8,
        "numericUnit": "millisecond"
      },
      "mainthread-work-breakdown": {
        "id": "mainthread-work-breakdown",
        "title": "Minimizes main-thread work",
        "description": "Consider reducing the time spent parsing, compiling and executing JS. You may find delivering smaller JS payloads helps with this. [Learn how to minimize main-thread work](https://developer.chrome.com/docs/lighthouse/performance/mainthread-work-breakdown/)",
        "score": 1,
        "scoreDisplayMode": "metricSavings",
        "displayValue": "1.1 s",
        "metricSavings": {
          "TBT": 150
        },
        "details": {
          "type": "table",
          "sortedBy": [
            "duration"
          ],
          "headings": [
            {
              "key": "groupLabel",
              "valueType": "text",
              "label": "Category"
            },
            {
              "key": "duration",
              "valueType": "ms",
              "label": "Time Spent",
              "granularity": 1
            }
          ],
          "items": [
            {
              "group": "scriptEvaluation",
              "duration": 921.88599999998235,
              "groupLabel": "Script Evaluation"
            },
            {
              "group": "other",
              "duration": 129.99800000000144,
              "groupLabel": "Other"
            },
            {
              "duration": 29.034000000000006,
              "groupLabel": "Style & Layout",
              "group": "styleLayout"
            },
            {
              "groupLabel": "Script Parsing & Compilation",
              "duration": 24.17700000000001,
              "group": "scriptParseCompile"
            },
            {
              "groupLabel": "Parse HTML & CSS",
              "duration": 6.3509999999999955,
              "group": "parseHTML"
            },
            {
              "groupLabel": "Garbage Collection",
              "group": "garbageCollection",
              "duration": 5.8359999999999976
            },
            {
              "duration": 5.0999999999999979,
              "group": "paintCompositeRender",
              "groupLabel": "Rendering"
            }
          ]
        },
        "numericValue": 1122.3819999999837,
        "numericUnit": "millisecond"
      },
      "has-hsts": {
        "id": "has-hsts",
        "title": "Use a strong HSTS policy",
        "description": "Deployment of the HSTS header significantly reduces the risk of downgrading HTTP connections and eavesdropping attacks. A rollout in stages, starting with a low max-age is recommended. [Learn more about using a strong HSTS policy.](https://developer.chrome.com/docs/lighthouse/best-practices/has-hsts)",
        "score": 1,
        "scoreDisplayMode": "informative",
        "details": {
          "type": "table",
          "items": [
            {
              "severity": "High",
              "description": "No HSTS header found"
            }
          ],
          "headings": [
            {
              "subItemsHeading": {
                "key": "description"
              },
              "label": "Description",
              "valueType": "text",
              "key": "description"
            },
            {
              "label": "Directive",
              "subItemsHeading": {
                "key": "directive"
              },
              "key": "directive",
              "valueType": "code"
            },
            {
              "subItemsHeading": {
                "key": "severity"
              },
              "valueType": "text",
              "label": "Severity",
              "key": "severity"
            }
          ]
        }
      },
      "third-party-facades": {
        "id": "third-party-facades",
        "title": "Lazy load third-party resources with facades",
        "description": "Some third-party embeds can be lazy loaded. Consider replacing them with a facade until they are required. [Learn how to defer third-parties with a facade](https://developer.chrome.com/docs/lighthouse/performance/third-party-facades/).",
        "score": null,
        "scoreDisplayMode": "notApplicable",
        "metricSavings": {
          "TBT": 0
        }
      },
      "form-field-multiple-labels": {
        "id": "form-field-multiple-labels",
        "title": "No form fields have multiple labels",
        "description": "Form fields with multiple labels can be confusingly announced by assistive technologies like screen readers which use either the first, the last, or all of the labels. [Learn how to use form labels](https://dequeuniversity.com/rules/axe/4.10/form-field-multiple-labels).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "aria-allowed-role": {
        "id": "aria-allowed-role",
        "title": "Uses ARIA roles only on compatible elements",
        "description": "Many HTML elements can only be assigned certain ARIA roles. Using ARIA roles where they are not allowed can interfere with the accessibility of the web page. [Learn more about ARIA roles](https://dequeuniversity.com/rules/axe/4.10/aria-allowed-role).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "doctype": {
        "id": "doctype",
        "title": "Page has the HTML doctype",
        "description": "Specifying a doctype prevents the browser from switching to quirks-mode. [Learn more about the doctype declaration](https://developer.chrome.com/docs/lighthouse/best-practices/doctype/).",
        "score": 1,
        "scoreDisplayMode": "binary"
      },
      "clickjacking-mitigation": {
        "id": "clickjacking-mitigation",
        "title": "Mitigate clickjacking with XFO or CSP",
        "description": "The `X-Frame-Options` (XFO) header or the `frame-ancestors` directive in the `Content-Security-Policy` (CSP) header control where a page can be embedded. These can mitigate clickjacking attacks by blocking some or all sites from embedding the page. [Learn more about mitigating clickjacking](https://developer.chrome.com/docs/lighthouse/best-practices/clickjacking-mitigation).",
        "score": 1,
        "scoreDisplayMode": "informative",
        "details": {
          "items": [
            {
              "description": "No frame control policy found",
              "severity": "High"
            }
          ],
          "type": "table",
          "headings": [
            {
              "key": "description",
              "subItemsHeading": {
                "key": "description"
              },
              "valueType": "text",
              "label": "Description"
            },
            {
              "valueType": "text",
              "label": "Severity",
              "key": "severity",
              "subItemsHeading": {
                "key": "severity"
              }
            }
          ]
        }
      },
      "color-contrast": {
        "id": "color-contrast",
        "title": "Background and foreground colors do not have a sufficient contrast ratio.",
        "description": "Low-contrast text is difficult or impossible for many users to read. [Learn how to provide sufficient color contrast](https://dequeuniversity.com/rules/axe/4.10/color-contrast).",
        "score": 0,
        "scoreDisplayMode": "binary",
        "details": {
          "type": "table",
          "items": [
            {
              "subItems": {
                "items": [
                  {
                    "relatedNode": {
                      "nodeLabel": "body#afd",
                      "selector": "body#afd",
                      "boundingRect": {
                        "height": 782,
                        "top": 16,
                        "left": 0,
                        "right": 1350,
                        "width": 1350,
                        "bottom": 798
                      },
                      "snippet": "<body id=\"afd\" style=\"visibility: visible;\">",
                      "lhId": "1-1-BODY",
                      "path": "1,HTML,1,BODY",
                      "type": "node"
                    }
                  }
                ],
                "type": "subitems"
              },
              "node": {
                "selector": "body#afd > div.wrapper1 > div.footer",
                "boundingRect": {
                  "top": 644,
                  "width": 472,
                  "right": 911,
                  "height": 154,
                  "bottom": 798,
                  "left": 439
                },
                "type": "node",
                "snippet": "<div class=\"footer\">",
                "explanation": "Fix any of the following:\n  Element has insufficient color contrast of 2.92 (foreground color: #626574, background color: #101c36, font size: 9.6pt (12.8px), font weight: normal). Expected contrast ratio of 4.5:1",
                "path": "1,HTML,1,BODY,2,DIV,4,DIV",
                "lhId": "1-0-DIV",
                "nodeLabel": "2025 Copyright | All Rights Reserved.\n\nPrivacy Policy\n\n\n\n"
              }
            },
            {
              "node": {
                "path": "1,HTML,1,BODY,2,DIV,4,DIV,3,A",
                "snippet": "<a href=\"javascript:void(0);\" onclick=\"window.open('/privacy.html', 'privacy-policy', 'width=890,height=330,left=…\" class=\"privacy-policy\">",
                "explanation": "Fix any of the following:\n  Element has insufficient color contrast of 2.92 (foreground color: #626574, background color: #101c36, font size: 9.6pt (12.8px), font weight: normal). Expected contrast ratio of 4.5:1",
                "nodeLabel": "Privacy Policy",
                "boundingRect": {
                  "left": 635,
                  "top": 706,
                  "height": 15,
                  "bottom": 721,
                  "right": 715,
                  "width": 80
                },
                "type": "node",
                "selector": "body#afd > div.wrapper1 > div.footer > a.privacy-policy",
                "lhId": "1-2-A"
              },
              "subItems": {
                "items": [
                  {
                    "relatedNode": {
                      "type": "node",
                      "nodeLabel": "body#afd",
                      "boundingRect": {
                        "bottom": 798,
                        "height": 782,
                        "left": 0,
                        "width": 1350,
                        "top": 16,
                        "right": 1350
                      },
                      "selector": "body#afd",
                      "path": "1,HTML,1,BODY",
                      "lhId": "1-1-BODY",
                      "snippet": "<body id=\"afd\" style=\"visibility: visible;\">"
                    }
                  }
                ],
                "type": "subitems"
              }
            }
          ],
          "debugData": {
            "type": "debugdata",
            "tags": [
              "cat.color",
              "wcag2aa",
              "wcag143",
              "TTv5",
              "TT13.c",
              "EN-301-549",
              "EN-9.1.4.3",
              "ACT"
            ],
            "impact": "serious"
          },
          "headings": [
            {
              "subItemsHeading": {
                "key": "relatedNode",
                "valueType": "node"
              },
              "key": "node",
              "label": "Failing Elements",
              "valueType": "node"
            }
          ]
        }
      },
      "aria-toggle-field-name": {
        "id": "aria-toggle-field-name",
        "title": "ARIA toggle fields have accessible names",
        "description": "When a toggle field doesn't have an accessible name, screen readers announce it with a generic name, making it unusable for users who rely on screen readers. [Learn more about toggle fields](https://dequeuniversity.com/rules/axe/4.10/aria-toggle-field-name).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "dlitem": {
        "id": "dlitem",
        "title": "Definition list items are wrapped in `<dl>` elements",
        "description": "Definition list items (`<dt>` and `<dd>`) must be wrapped in a parent `<dl>` element to ensure that screen readers can properly announce them. [Learn how to structure definition lists correctly](https://dequeuniversity.com/rules/axe/4.10/dlitem).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "label": {
        "id": "label",
        "title": "Form elements have associated labels",
        "description": "Labels ensure that form controls are announced properly by assistive technologies, like screen readers. [Learn more about form element labels](https://dequeuniversity.com/rules/axe/4.10/label).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "canonical": {
        "id": "canonical",
        "title": "Document has a valid `rel=canonical`",
        "description": "Canonical links suggest which URL to show in search results. [Learn more about canonical links](https://developer.chrome.com/docs/lighthouse/seo/canonical/).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "final-screenshot": {
        "id": "final-screenshot",
        "title": "Final Screenshot",
        "description": "The last screenshot captured of the pageload.",
        "score": 1,
        "scoreDisplayMode": "informative",
        "details": {
          "timestamp": 6426909051827,
          "timing": 3008,
          "type": "screenshot",
          "data": "data:image/jpeg;base64,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"
        }
      },
      "aria-roles": {
        "id": "aria-roles",
        "title": "`[role]` values are valid",
        "description": "ARIA roles must have valid values in order to perform their intended accessibility functions. [Learn more about valid ARIA roles](https://dequeuniversity.com/rules/axe/4.10/aria-roles).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "total-byte-weight": {
        "id": "total-byte-weight",
        "title": "Avoids enormous network payloads",
        "description": "Large network payloads cost users real money and are highly correlated with long load times. [Learn how to reduce payload sizes](https://developer.chrome.com/docs/lighthouse/performance/total-byte-weight/).",
        "score": 1,
        "scoreDisplayMode": "metricSavings",
        "displayValue": "Total size was 273 KiB",
        "details": {
          "type": "table",
          "headings": [
            {
              "key": "url",
              "label": "URL",
              "valueType": "url"
            },
            {
              "valueType": "bytes",
              "label": "Transfer Size",
              "key": "totalBytes"
            }
          ],
          "sortedBy": [
            "totalBytes"
          ],
          "items": [
            {
              "url": "http://www.google.com/adsense/domains/caf.js?abp=1&adsdeli=true",
              "totalBytes": 58391
            },
            {
              "totalBytes": 58321,
              "url": "https://syndicatedsearch.goog/adsense/domains/caf.js?pac=2"
            },
            {
              "url": "https://euob.youseasky.com/sxp/i/224f85302aa2b6ec30aac9a85da2cbf9.js",
              "totalBytes": 43713
            },
            {
              "totalBytes": 23076,
              "url": "https://www.google.com/js/bg/Z-SsKYkj_Kr8t4L84tyvkiZZMnLnK5CX23Vh5jPe2Hs.js"
            },
            {
              "url": "https://pagead2.googlesyndication.com/bg/qoxIykLQHporMav0XsqS8NtTd2boZuUJaM-UYWb_7aA.js",
              "totalBytes": 21934
            },
            {
              "totalBytes": 12658,
              "url": "https://syndicatedsearch.goog/afs/ads?adtest=off&psid=5837883959&pcsa=false&channel=000001%2Cbucket011%2Cbucket088&client=dp-teaminternet09_3ph&r=m&hl=en&rpbu=http%3A%2F%2Fwww.se1gym.co.uk%2F%3Fts%3DeyJhbGciOiJBMTI4S1ciLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0.NeKCl3434-fhnmpc7JzRjCIdVoTiSfuwVUEP2Yc-gsu0HmXc_vsFTA.6kyd_O5XT-3k6ObkEsqreg.fOjYJ2KQRB3woJ80Rozyk2zFzhL9IPaY7o0LHDPtW1pnYYwwU3Cey0UOleqiaRcI7K3h55qGWt5SDInzQbKeoYJ-RcjosmWtvgh6jfv0ah4_GTjhVamXOaufcI5E5Pv7FGXwmkt1xEO9TNeMVY7ZLZxUax-NhPw96WaiJZ0uWS3NLXuC_EuaYhmZ89c2Vw2mqMUtACT9lo-5nk4KEc47Sm9v115JGjhEmA4C9ipzAIkv1AqLse02jhlhRERJ2v0fbe3m5U3htU-fmk99vA_m1hx0e9-pcTq_CiSeuTPhtOaikysaC5k5LnEEnb01s6Ypk4i7UH7ZvegMUTLWq_8_0Elwy1KmGZFz51nQMFYvyBYAy4REN6bLeEAPvW45JVNfRBFlebEYXifkv9lt_vDqYlkSt7vFLJO8rUEOm7NXsKw-xwHuJaYp2k4urADKZnrFN8dyI04omA0wPaLcMdzI2-LQsUSbVQvDI-iWO-UWT9XkzYu97yNN7X-01fS-pRZWAkqFd_EVVqjBCwVsiinH17tDuoRZwDbxsPbs43DU4qlxXQgyp7giZeuMDKqrsDNDxCTC8fF8TKVR3tFHqurLq-7mZh_g3SE8uKEGIFwVOQREJ_l1V41r70RvpW67Twx-.nn00YuV_rZifffKjlJ4rzQ&type=3&swp=as-drid-2841604693446448&oe=UTF-8&ie=UTF-8&fexp=21404%2C17300002%2C17301437%2C17301439%2C17301442%2C17301548%2C17301266%2C72717108%2C73027842&format=r3%7Cs&nocache=1231756150223801&num=0&output=afd_ads&domain_name=www.se1gym.co.uk&v=3&bsl=8&pac=2&u_his=2&u_tz=-420&dt=1756150223803&u_w=800&u_h=600&biw=1350&bih=940&psw=1350&psh=754&frm=0&uio=--&cont=tc&drt=0&jsid=caf&nfp=1&jsv=796426389&rurl=http%3A%2F%2Fwww.se1gym.co.uk%2F"
            },
            {
              "totalBytes": 11993,
              "url": "http://d38psrni17bvxu.cloudfront.net/fonts/Port_Lligat_Slab/latin.woff2"
            },
            {
              "url": "http://d38psrni17bvxu.cloudfront.net/themes/cleanPeppermintBlack_657d9013/img/arrows.png",
              "totalBytes": 11842
            },
            {
              "url": "https://ep2.adtrafficquality.google/sodar/sodar2.js",
              "totalBytes": 7852
            },
            {
              "url": "http://www.se1gym.co.uk/",
              "totalBytes": 7768
            }
          ]
        },
        "numericValue": 279276,
        "numericUnit": "byte"
      },
      "viewport-insight": {
        "id": "viewport-insight",
        "title": "Optimize viewport for mobile",
        "description": "Tap interactions may be [delayed by up to 300 ms](https://developer.chrome.com/blog/300ms-tap-delay-gone-away/) if the viewport is not optimized for mobile.",
        "score": 1,
        "scoreDisplayMode": "numeric",
        "metricSavings": {
          "INP": 0
        },
        "details": {
          "headings": [
            {
              "key": "node",
              "valueType": "node"
            }
          ],
          "type": "table",
          "items": [
            {
              "node": {
                "type": "node",
                "nodeLabel": "head > meta",
                "path": "1,HTML,0,HEAD,1,META",
                "selector": "head > meta",
                "boundingRect": {
                  "bottom": 0,
                  "width": 0,
                  "height": 0,
                  "right": 0,
                  "top": 0,
                  "left": 0
                },
                "lhId": "page-3-META",
                "snippet": "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, shrink-to-fit=no\">"
              }
            }
          ]
        }
      },
      "user-timings": {
        "id": "user-timings",
        "title": "User Timing marks and measures",
        "description": "Consider instrumenting your app with the User Timing API to measure your app's real-world performance during key user experiences. [Learn more about User Timing marks](https://developer.chrome.com/docs/lighthouse/performance/user-timings/).",
        "score": null,
        "scoreDisplayMode": "notApplicable",
        "details": {
          "items": [],
          "headings": [
            {
              "key": "name",
              "label": "Name",
              "valueType": "text"
            },
            {
              "label": "Type",
              "key": "timingType",
              "valueType": "text"
            },
            {
              "key": "startTime",
              "granularity": 0.01,
              "label": "Start Time",
              "valueType": "ms"
            },
            {
              "label": "Duration",
              "granularity": 0.01,
              "key": "duration",
              "valueType": "ms"
            }
          ],
          "type": "table"
        }
      },
      "metrics": {
        "id": "metrics",
        "title": "Metrics",
        "description": "Collects all available metrics.",
        "score": 1,
        "scoreDisplayMode": "informative",
        "details": {
          "type": "debugdata",
          "items": [
            {
              "observedSpeedIndexTs": 6426908582852,
              "observedLastVisualChange": 3007,
              "observedLastVisualChangeTs": 6426909050855,
              "observedFirstVisualChange": 2435,
              "firstContentfulPaint": 400,
              "observedDomContentLoaded": 2417,
              "observedNavigationStart": 0,
              "observedFirstContentfulPaint": 2435,
              "timeToFirstByte": 121,
              "observedDomContentLoadedTs": 6426908460372,
              "observedTraceEndTs": 6426914804078,
              "maxPotentialFID": 136,
              "observedLoad": 3022,
              "observedCumulativeLayoutShiftMainFrame": 0.0014474920852919878,
              "observedTraceEnd": 8760,
              "observedFirstContentfulPaintTs": 6426908478989,
              "observedFirstPaintTs": 6426908478989,
              "observedNavigationStartTs": 6426906043855,
              "observedLargestContentfulPaintAllFrames": 2488,
              "observedSpeedIndex": 2539,
              "observedLargestContentfulPaintAllFramesTs": 6426908531800,
              "speedIndex": 1759,
              "cumulativeLayoutShiftMainFrame": 0.0014474920852919878,
              "observedLargestContentfulPaint": 2488,
              "observedFirstContentfulPaintAllFramesTs": 6426908478989,
              "observedFirstPaint": 2435,
              "observedFirstVisualChangeTs": 6426908478855,
              "interactive": 1174,
              "observedTimeOriginTs": 6426906043855,
              "lcpLoadStart": 496,
              "observedLargestContentfulPaintTs": 6426908531800,
              "cumulativeLayoutShift": 0.0014474920852919878,
              "lcpLoadEnd": 503,
              "observedLoadTs": 6426909065896,
              "observedTimeOrigin": 0,
              "observedCumulativeLayoutShift": 0.0014474920852919878,
              "observedFirstContentfulPaintAllFrames": 2435,
              "largestContentfulPaint": 513,
              "totalBlockingTime": 143
            },
            {
              "lcpInvalidated": false
            }
          ]
        },
        "numericValue": 1174,
        "numericUnit": "millisecond"
      },
      "lcp-lazy-loaded": {
        "id": "lcp-lazy-loaded",
        "title": "Largest Contentful Paint image was not lazily loaded",
        "description": "Above-the-fold images that are lazily loaded render later in the page lifecycle, which can delay the largest contentful paint. [Learn more about optimal lazy loading](https://web.dev/articles/lcp-lazy-loading).",
        "score": 1,
        "scoreDisplayMode": "metricSavings",
        "metricSavings": {
          "LCP": 0
        },
        "details": {
          "headings": [
            {
              "key": "node",
              "valueType": "node",
              "label": "Element"
            }
          ],
          "items": [
            {
              "node": {
                "selector": "body#afd > div.wrapper1 > div.wrapper2",
                "snippet": "<div class=\"wrapper2\">",
                "lhId": "1-8-DIV",
                "type": "node",
                "path": "1,HTML,1,BODY,2,DIV,3,DIV",
                "boundingRect": {
                  "left": 0,
                  "right": 1350,
                  "bottom": 628,
                  "top": 16,
                  "height": 612,
                  "width": 1350
                },
                "nodeLabel": "\n\n\nse1gym.co.uk"
              }
            }
          ],
          "type": "table"
        }
      },
      "lcp-discovery-insight": {
        "id": "lcp-discovery-insight",
        "title": "LCP request discovery",
        "description": "Optimize LCP by making the LCP image [discoverable](https://web.dev/articles/optimize-lcp#1_eliminate_resource_load_delay) from the HTML immediately, and [avoiding lazy-loading](https://web.dev/articles/lcp-lazy-loading)",
        "score": 0,
        "scoreDisplayMode": "numeric",
        "metricSavings": {
          "LCP": 0
        },
        "details": {
          "type": "list",
          "items": [
            {
              "items": {
                "requestDiscoverable": {
                  "value": true,
                  "label": "Request is discoverable in initial document"
                },
                "priorityHinted": {
                  "value": false,
                  "label": "fetchpriority=high should be applied"
                },
                "eagerlyLoaded": {
                  "label": "lazy load not applied",
                  "value": true
                }
              },
              "type": "checklist"
            },
            {
              "selector": "body#afd > div.wrapper1 > div.wrapper2",
              "snippet": "<div class=\"wrapper2\">",
              "lhId": "page-0-DIV",
              "path": "1,HTML,1,BODY,2,DIV,3,DIV",
              "boundingRect": {
                "bottom": 628,
                "width": 1350,
                "height": 612,
                "right": 1350,
                "top": 16,
                "left": 0
              },
              "type": "node",
              "nodeLabel": "\n\n\nse1gym.co.uk"
            }
          ]
        }
      },
      "long-tasks": {
        "id": "long-tasks",
        "title": "Avoid long main-thread tasks",
        "description": "Lists the longest tasks on the main thread, useful for identifying worst contributors to input delay. [Learn how to avoid long main-thread tasks](https://web.dev/articles/optimize-long-tasks)",
        "score": 1,
        "scoreDisplayMode": "informative",
        "displayValue": "3 long tasks found",
        "metricSavings": {
          "TBT": 150
        },
        "details": {
          "skipSumming": [
            "startTime"
          ],
          "headings": [
            {
              "label": "URL",
              "valueType": "url",
              "key": "url"
            },
            {
              "key": "startTime",
              "label": "Start Time",
              "valueType": "ms",
              "granularity": 1
            },
            {
              "valueType": "ms",
              "granularity": 1,
              "key": "duration",
              "label": "Duration"
            }
          ],
          "debugData": {
            "tasks": [
              {
                "other": 208,
                "duration": 208,
                "parseHTML": 0,
                "urlIndex": 0,
                "startTime": 167.8
              },
              {
                "other": 136,
                "urlIndex": 1,
                "scriptEvaluation": 0,
                "duration": 136,
                "startTime": 1048.4
              },
              {
                "urlIndex": 2,
                "other": 118,
                "startTime": 530.8,
                "duration": 118
              }
            ],
            "type": "debugdata",
            "urls": [
              "http://www.se1gym.co.uk/",
              "https://www.google.com/js/bg/Z-SsKYkj_Kr8t4L84tyvkiZZMnLnK5CX23Vh5jPe2Hs.js",
              "http://www.google.com/adsense/domains/caf.js?abp=1&adsdeli=true"
            ]
          },
          "items": [
            {
              "duration": 208,
              "startTime": 167.83807490074116,
              "url": "http://www.se1gym.co.uk/"
            },
            {
              "url": "https://www.google.com/js/bg/Z-SsKYkj_Kr8t4L84tyvkiZZMnLnK5CX23Vh5jPe2Hs.js",
              "startTime": 1048.4384381877262,
              "duration": 136
            },
            {
              "startTime": 530.838698673609,
              "url": "http://www.google.com/adsense/domains/caf.js?abp=1&adsdeli=true",
              "duration": 118
            }
          ],
          "sortedBy": [
            "duration"
          ],
          "type": "table"
        }
      },
      "accesskeys": {
        "id": "accesskeys",
        "title": "`[accesskey]` values are unique",
        "description": "Access keys let users quickly focus a part of the page. For proper navigation, each access key must be unique. [Learn more about access keys](https://dequeuniversity.com/rules/axe/4.10/accesskeys).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "critical-request-chains": {
        "id": "critical-request-chains",
        "title": "Avoid chaining critical requests",
        "description": "The Critical Request Chains below show you what resources are loaded with a high priority. Consider reducing the length of chains, reducing the download size of resources, or deferring the download of unnecessary resources to improve page load. [Learn how to avoid chaining critical requests](https://developer.chrome.com/docs/lighthouse/performance/critical-request-chains/).",
        "score": 1,
        "scoreDisplayMode": "informative",
        "displayValue": "1 chain found",
        "details": {
          "type": "criticalrequestchain",
          "longestChain": {
            "length": 2,
            "transferSize": 11993,
            "duration": 2436.5970001220703
          },
          "chains": {
            "2B324D57CB20BDFACF936725E1BD71D4": {
              "request": {
                "responseReceivedTime": 6426908.2295349995,
                "endTime": 6426908.229539,
                "transferSize": 7768,
                "startTime": 6426906.044813,
                "url": "http://www.se1gym.co.uk/"
              },
              "children": {
                "52.5": {
                  "request": {
                    "responseReceivedTime": 6426908.4814059995,
                    "endTime": 6426908.48141,
                    "url": "http://d38psrni17bvxu.cloudfront.net/fonts/Port_Lligat_Slab/latin.woff2",
                    "startTime": 6426908.451117,
                    "transferSize": 11993
                  }
                }
              }
            }
          }
        }
      },
      "video-caption": {
        "id": "video-caption",
        "title": "`<video>` elements contain a `<track>` element with `[kind=\"captions\"]`",
        "description": "When a video provides a caption it is easier for deaf and hearing impaired users to access its information. [Learn more about video captions](https://dequeuniversity.com/rules/axe/4.10/video-caption).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "uses-optimized-images": {
        "id": "uses-optimized-images",
        "title": "Efficiently encode images",
        "description": "Optimized images load faster and consume less cellular data. [Learn how to efficiently encode images](https://developer.chrome.com/docs/lighthouse/performance/uses-optimized-images/).",
        "score": 1,
        "scoreDisplayMode": "metricSavings",
        "metricSavings": {
          "LCP": 0,
          "FCP": 0
        },
        "details": {
          "overallSavingsBytes": 0,
          "sortedBy": [
            "wastedBytes"
          ],
          "headings": [],
          "overallSavingsMs": 0,
          "type": "opportunity",
          "items": [],
          "debugData": {
            "metricSavings": {
              "LCP": 0,
              "FCP": 0
            },
            "type": "debugdata"
          }
        },
        "warnings": [],
        "numericValue": 0,
        "numericUnit": "millisecond"
      },
      "aria-valid-attr": {
        "id": "aria-valid-attr",
        "title": "`[aria-*]` attributes are valid and not misspelled",
        "description": "Assistive technologies, like screen readers, can't interpret ARIA attributes with invalid names. [Learn more about valid ARIA attributes](https://dequeuniversity.com/rules/axe/4.10/aria-valid-attr).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "aria-required-parent": {
        "id": "aria-required-parent",
        "title": "`[role]`s are contained by their required parent element",
        "description": "Some ARIA child roles must be contained by specific parent roles to properly perform their intended accessibility functions. [Learn more about ARIA roles and required parent element](https://dequeuniversity.com/rules/axe/4.10/aria-required-parent).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "first-meaningful-paint": {
        "id": "first-meaningful-paint",
        "title": "First Meaningful Paint",
        "description": "First Meaningful Paint measures when the primary content of a page is visible. [Learn more about the First Meaningful Paint metric](https://developer.chrome.com/docs/lighthouse/performance/first-meaningful-paint/).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "focusable-controls": {
        "id": "focusable-controls",
        "title": "Interactive controls are keyboard focusable",
        "description": "Custom interactive controls are keyboard focusable and display a focus indicator. [Learn how to make custom controls focusable](https://developer.chrome.com/docs/lighthouse/accessibility/focusable-controls/).",
        "score": null,
        "scoreDisplayMode": "manual"
      },
      "third-party-summary": {
        "id": "third-party-summary",
        "title": "Minimize third-party usage",
        "description": "Third-party code can significantly impact load performance. Limit the number of redundant third-party providers and try to load third-party code after your page has primarily finished loading. [Learn how to minimize third-party impact](https://developers.google.com/web/fundamentals/performance/optimizing-content-efficiency/loading-third-party-javascript/).",
        "score": 1,
        "scoreDisplayMode": "informative",
        "displayValue": "Third-party code blocked the main thread for 150 ms",
        "metricSavings": {
          "TBT": 150
        },
        "details": {
          "summary": {
            "wastedMs": 154.00000000000003,
            "wastedBytes": 270432
          },
          "items": [
            {
              "tbtImpact": 79.211009309342785,
              "mainThreadTime": 167.71399999999852,
              "subItems": {
                "items": [
                  {
                    "tbtImpact": 79.211009309342785,
                    "transferSize": 58321,
                    "mainThreadTime": 160.50299999999851,
                    "url": "https://syndicatedsearch.goog/adsense/domains/caf.js?pac=2",
                    "blockingTime": 79.211009309342785
                  },
                  {
                    "url": "https://syndicatedsearch.goog/afs/ads?adtest=off&psid=5837883959&pcsa=false&channel=000001%2Cbucket011%2Cbucket088&client=dp-teaminternet09_3ph&r=m&hl=en&rpbu=http%3A%2F%2Fwww.se1gym.co.uk%2F%3Fts%3DeyJhbGciOiJBMTI4S1ciLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0.NeKCl3434-fhnmpc7JzRjCIdVoTiSfuwVUEP2Yc-gsu0HmXc_vsFTA.6kyd_O5XT-3k6ObkEsqreg.fOjYJ2KQRB3woJ80Rozyk2zFzhL9IPaY7o0LHDPtW1pnYYwwU3Cey0UOleqiaRcI7K3h55qGWt5SDInzQbKeoYJ-RcjosmWtvgh6jfv0ah4_GTjhVamXOaufcI5E5Pv7FGXwmkt1xEO9TNeMVY7ZLZxUax-NhPw96WaiJZ0uWS3NLXuC_EuaYhmZ89c2Vw2mqMUtACT9lo-5nk4KEc47Sm9v115JGjhEmA4C9ipzAIkv1AqLse02jhlhRERJ2v0fbe3m5U3htU-fmk99vA_m1hx0e9-pcTq_CiSeuTPhtOaikysaC5k5LnEEnb01s6Ypk4i7UH7ZvegMUTLWq_8_0Elwy1KmGZFz51nQMFYvyBYAy4REN6bLeEAPvW45JVNfRBFlebEYXifkv9lt_vDqYlkSt7vFLJO8rUEOm7NXsKw-xwHuJaYp2k4urADKZnrFN8dyI04omA0wPaLcMdzI2-LQsUSbVQvDI-iWO-UWT9XkzYu97yNN7X-01fS-pRZWAkqFd_EVVqjBCwVsiinH17tDuoRZwDbxsPbs43DU4qlxXQgyp7giZeuMDKqrsDNDxCTC8fF8TKVR3tFHqurLq-7mZh_g3SE8uKEGIFwVOQREJ_l1V41r70RvpW67Twx-.nn00YuV_rZifffKjlJ4rzQ&type=3&swp=as-drid-2841604693446448&oe=UTF-8&ie=UTF-8&fexp=21404%2C17300002%2C17301437%2C17301439%2C17301442%2C17301548%2C17301266%2C72717108%2C73027842&format=r3%7Cs&nocache=1231756150223801&num=0&output=afd_ads&domain_name=www.se1gym.co.uk&v=3&bsl=8&pac=2&u_his=2&u_tz=-420&dt=1756150223803&u_w=800&u_h=600&biw=1350&bih=940&psw=1350&psh=754&frm=0&uio=--&cont=tc&drt=0&jsid=caf&nfp=1&jsv=796426389&rurl=http%3A%2F%2Fwww.se1gym.co.uk%2F",
                    "blockingTime": 0,
                    "mainThreadTime": 7.211,
                    "tbtImpact": 0,
                    "transferSize": 12658
                  },
                  {
                    "transferSize": 664,
                    "url": "https://syndicatedsearch.goog/afs/gen_204?client=dp-teaminternet09_3ph&output=uds_ads_only&zx=ln713idy80hw&cd_fexp=72717108%2C73027842&aqid=z7msaPCANfHZywXK5ZegAg&psid=5837883959&pbt=ri&emsg=sodar_latency&rt=1.8999996185302734&ea=10",
                    "tbtImpact": 0,
                    "blockingTime": 0,
                    "mainThreadTime": 0
                  },
                  {
                    "url": "https://syndicatedsearch.goog/afs/gen_204?client=dp-teaminternet09_3ph&output=uds_ads_only&zx=4ouv3ygraqj9&cd_fexp=72717108%2C73027842&aqid=z7msaPCANfHZywXK5ZegAg&psid=5837883959&pbt=bs&adbx=410&adby=129&adbh=498&adbw=530&adbah=160%2C160%2C160&adbn=master-1&eawp=partner-dp-teaminternet09_3ph&errv=796426389&csala=9%7C0%7C133%7C35%7C133&lle=0&ifv=1&hpt=1",
                    "blockingTime": 0,
                    "tbtImpact": 0,
                    "transferSize": 664,
                    "mainThreadTime": 0
                  },
                  {
                    "blockingTime": 0,
                    "transferSize": 664,
                    "url": "https://syndicatedsearch.goog/afs/gen_204?client=dp-teaminternet09_3ph&output=uds_ads_only&zx=h02t5ltnisir&cd_fexp=72717108%2C73027842&aqid=z7msaPCANfHZywXK5ZegAg&psid=5837883959&pbt=bv&adbx=410&adby=129&adbh=498&adbw=530&adbah=160%2C160%2C160&adbn=master-1&eawp=partner-dp-teaminternet09_3ph&errv=796426389&csala=9%7C0%7C133%7C35%7C133&lle=0&ifv=1&hpt=1",
                    "mainThreadTime": 0,
                    "tbtImpact": 0
                  }
                ],
                "type": "subitems"
              },
              "transferSize": 72971,
              "blockingTime": 79.211009309342785,
              "entity": "syndicatedsearch.goog"
            },
            {
              "entity": "Other Google APIs/SDKs",
              "mainThreadTime": 255.15999999999764,
              "tbtImpact": 74.788990690657243,
              "transferSize": 81467,
              "subItems": {
                "type": "subitems",
                "items": [
                  {
                    "transferSize": 58391,
                    "url": "http://www.google.com/adsense/domains/caf.js?abp=1&adsdeli=true",
                    "blockingTime": 68,
                    "tbtImpact": 68,
                    "mainThreadTime": 244.43299999999763
                  },
                  {
                    "blockingTime": 6.7889906906572381,
                    "mainThreadTime": 10.726999999999999,
                    "transferSize": 23076,
                    "tbtImpact": 6.7889906906572381,
                    "url": "https://www.google.com/js/bg/Z-SsKYkj_Kr8t4L84tyvkiZZMnLnK5CX23Vh5jPe2Hs.js"
                  }
                ]
              },
              "blockingTime": 74.788990690657243
            },
            {
              "transferSize": 46422,
              "entity": "youseasky.com",
              "mainThreadTime": 183.06799999999978,
              "blockingTime": 0,
              "tbtImpact": 0,
              "subItems": {
                "items": [
                  {
                    "blockingTime": 0,
                    "transferSize": 43713,
                    "tbtImpact": 0,
                    "mainThreadTime": 157.44399999999979,
                    "url": "https://euob.youseasky.com/sxp/i/224f85302aa2b6ec30aac9a85da2cbf9.js"
                  },
                  {
                    "url": "https://obseu.youseasky.com/ct?id=80705&url=http%3A%2F%2Fwww.se1gym.co.uk%2F&sf=0&tpi=&ch=AdsDeli%20-%20domain%20-%20landingpage&uvid=9c4a9c1eafd7b052958cfc9bf1bd90941639b350&tsf=0&tsfmi=&tsfu=&cb=1756150223905&hl=2&op=0&ag=2731360679&rand=739255181577657701061820315677051408075158159128090655675510012196508605616879696829621662&fs=1350x940&fst=1350x940&np=linux%20x86_64&nv=google%20inc.&ref=&ss=800x600&nc=0&at=&di=W1siZWYiLDkyNDldLFsiYWJuY2giLDIwXSxbLTYsIntcIndcIjpbXCIwXCIsXCJ0Y2Jsb2NrXCIsXCJzZWFyY2hib3hCbG9ja1wiLFwiZ2V0WE1MaHR0cFwiLFwiYWpheFF1ZXJ5XCIsXCJhamF4QmFja2ZpbGxcIixcImxvYWRGZWVkXCIsXCJ4bWxIdHRwXCIsXCJsc1wiLFwiZ2V0TG9hZEZlZWRBcmd1bWVudHNcIixcIl9fY3RjZ19jdF84MDcwNV9leGVjXCJdLFwiblwiOltdLFwiZFwiOltdfSJdLFstNywiLSJdLFstMTIsIm51bGwiXSxbLTE4LCJbMCwwLDAsMV0iXSxbLTQ2LCIwIl0sWy01NywiV0UwWmVFdExXRUFYVkZ3WkVWRk5UVWxLQXhZV1hFeFdXeGRBVmt4S1hGaEtVa0FYV2xaVUZrcEJTUlpRRmdzTERWOEJEQW9KQzFoWUMxc1BYRm9LQ1ZoWVdnQllBUXhkV0F0YVcxOEFGMU5LQXdnRER3a0xEQTBRRlZoTkdVc1pFVkZOVFVsS0F4WVdYRXhXV3hkQVZreEtYRmhLVWtBWFdsWlVGa3BCU1JaUUZnc0xEVjhCREFvSkMxaFlDMXNQWEZvS0NWaFlXZ0JZQVF4ZFdBdGFXMThBRjFOS0F3Z0REd3dNREFBUSJdLFstNjEsIi0iXSxbLTczLCJFaFE9Il0sWy0yNCwiW10iXSxbLTEwLCItIl0sWy0xMywiLSJdLFstMiwiMTIsZWNYRlgxLzdudHZUZGxXN0s3NlNFRUNDRUpCQVJFV3VpZzBsRUlTQmNRUlVGQlFlbWhpQ0NJU3BVcUlJalNPMUlOaUNLOXBpY2tJVDJiYko5NTVkNTc3djkzM3N6Ym5Td0pJUCJdLFstMzIsIjAiXSxbLTQxLCItIl0sWy02MiwiODAiXSxbLTQsIi0iXSxbLTUsIi0iXSxbLTQ0LCIwLDAsMCw1Il0sWy05LCIrIl0sWzEyLCJ7XCJjdHhcIjpcIndlYmdsXCIsXCJ2XCI6XCJnb29nbGUgaW5jLiAoZ29vZ2xlKVwiLFwiclwiOlwiYW5nbGUgKGdvb2dsZSwgdnVsa2FuIDEuMy4wIChzd2lmdHNoYWRlciBkZXZpY2UgKHN1Ynplcm8pICgweDAwMDBjMGRlKSksIHN3aWZ0c2hhZGVyIGRyaXZlcilcIixcInNsdlwiOlwid2ViZ2wgZ2xzbCBlcyAxLjAgKG9wZW5nbCBlcyBnbHNsIGVzIDEuMCBjaHJvbWl1bSlcIixcImd2ZXJcIjpcIndlYmdsIDEuMCAob3BlbmdsIGVzIDIuMCBjaHJvbWl1bSlcIixcImd2ZW5cIjpcIndlYmtpdFwiLFwiYmVuXCI6MTAsXCJ3Z2xcIjoxLFwiZ3JlblwiOlwid2Via2l0IHdlYmdsXCIsXCJzZWZcIjoxOTMwODIwMjc5LFwic2VjXCI6XCJcIn0iXSxbLTUwLCItIl0sWy01MSwiLSJdLFstMzMsIi0iXSxbLTU2LCJsYW5kc2NhcGUtcHJpbWFyeSJdLFstMzYsIltcIjQvM1wiLFwiNC8zXCJdIl0sWy0xNiwiMCJdLFstNDgsIltcIi1cIixcIi1cIixcIi1cIixcIi1cIixcIi1cIl0iXSxbLTQ5LCItIl0sWy0yOCwiZW4tVVMiXSxbLTI5LCItIl0sWy0zMSwiZmFsc2UiXSxbLTM0LCItIl0sWy0xNCwiLSJdLFstMzUsIlsxNzU2MTUwMjIzODQxLDddIl0sWy00MiwiODgzMzk5MDE2Il0sWy02NSwiLSJdLFstNTIsIi0iXSxbLTE1LCItIl0sWy01OSwiZGVuaWVkIl0sWy0zOCwiaSwtMSwtMSwwLDAsMCwwLDAsMCwyMTg2LC0xLDAsLCwyNTQzLDI1NDQiXSxbLTYwLCItIl0sWy0yMSwiLSJdLFstMjMsIisiXSxbLTE3LCI1NiJdLFstNDAsIjMzIl0sWy02MywiMTYiXSxbLTQ1LCI2MjAsMCwwLDAsMCw1NjIsMCwwLDY0OCw1ODMsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCJdLFstMjUsIi0iXSxbLTExLCJ7XCJ0XCI6XCJcIixcIm1cIjpbXCJkZXNjcmlwdGlvblwiXX0iXSxbLTMwLCJbXCJ2XCIsMF0iXSxbLTY4LCItIl0sWy01NCwie1wiaFwiOltcIjMyOTk3Mjg0NTJcIixcIjgyMjgyMzExOVwiLFwiXzNcIixcIjI4NzI4OTkzMjBcIl0sXCJkXCI6W10sXCJiXCI6W1wiXzBcIixcIjI2NDYwMzg4MlwiXSxcInNcIjoxfSJdLFstMSwiLSJdLFstMywiW10iXSxbLTIwLCItIl0sWy00NywiQW1lcmljYS9Mb3NfQW5nZWxlcyxlbi1VUyxsYXRuLGdyZWdvcnkiXSxbLTgsIi0iXSxbLTI3LCJbMCwxMCwwLFwiNGdcIixudWxsXSJdLFstNjYsImdlb2xvY2F0aW9uLGNodWFmdWxsdmVyc2lvbmxpc3QsY3Jvc3NvcmlnaW5pc29sYXRlZCxzY3JlZW53YWtlbG9jayxwdWJsaWNrZXljcmVkZW50aWFsc2dldCxzaGFyZWRzdG9yYWdlc2VsZWN0dXJsLGNodWFhcmNoLGNvbXB1dGVwcmVzc3VyZSxjaHByZWZlcnNyZWR1Y2VkdHJhbnNwYXJlbmN5LGRlZmVycmVkZmV0Y2gsdXNiLGNoc2F2ZWRhdGEscHVibGlja2V5Y3JlZGVudGlhbHNjcmVhdGUsc2hhcmVkc3RvcmFnZSxkZWZlcnJlZGZldGNobWluaW1hbCxydW5hZGF1Y3Rpb24sY2hkb3dubGluayxjaHVhZm9ybWZhY3RvcnMsb3RwY3JlZGVudGlhbHMscGF5bWVudCxjaHVhLGNodWFtb2RlbCxjaGVjdCxhdXRvcGxheSxjYW1lcmEscHJpdmF0ZXN0YXRldG9rZW5pc3N1YW5jZSxhY2NlbGVyb21ldGVyLGNodWFwbGF0Zm9ybXZlcnNpb24saWRsZWRldGVjdGlvbixwcml2YXRlYWdncmVnYXRpb24saW50ZXJlc3Rjb2hvcnQsY2h2aWV3cG9ydGhlaWdodCxjYXB0dXJlZHN1cmZhY2Vjb250cm9sLGxvY2FsZm9udHMsY2h1YXBsYXRmb3JtLG1pZGksY2h1YWZ1bGx2ZXJzaW9uLHhyc3BhdGlhbHRyYWNraW5nLGNsaXBib2FyZHJlYWQsZ2FtZXBhZCxkaXNwbGF5Y2FwdHVyZSxrZXlib2FyZG1hcCxqb2luYWRpbnRlcmVzdGdyb3VwLGNod2lkdGgsY2hwcmVmZXJzcmVkdWNlZG1vdGlvbixicm93c2luZ3RvcGljcyxlbmNyeXB0ZWRtZWRpYSxneXJvc2NvcGUsc2VyaWFsLGNocnR0LGNodWFtb2JpbGUsd2luZG93bWFuYWdlbWVudCx1bmxvYWQsY2hkcHIsY2hwcmVmZXJzY29sb3JzY2hlbWUsY2h1YXdvdzY0LGF0dHJpYnV0aW9ucmVwb3J0aW5nLGZ1bGxzY3JlZW4saWRlbnRpdHljcmVkZW50aWFsc2dldCxwcml2YXRlc3RhdGV0b2tlbnJlZGVtcHRpb24saGlkLGNodWFiaXRuZXNzLHN0b3JhZ2VhY2Nlc3Msc3luY3hocixjaGRldmljZW1lbW9yeSxjaHZpZXdwb3J0d2lkdGgscGljdHVyZWlucGljdHVyZSxtYWduZXRvbWV0ZXIsY2xpcGJvYXJkd3JpdGUsbWljcm9waG9uZSJdLFstNjcsIi0iXSxbImJuY2giLDE3NF0sWy0zNywiLSJdLFstMzksIltcIjIwMDMwMTA3XCIsMCxcIkdlY2tvXCIsXCJOZXRzY2FwZVwiLFwiTW96aWxsYVwiLG51bGwsbnVsbCxmYWxzZSxudWxsLGZhbHNlLG51bGwsMCxmYWxzZSxmYWxzZSxudWxsLDAsZmFsc2UsZmFsc2UsZmFsc2UsdHJ1ZV0iXSxbLTQzLCIwMDAwMDAwMTAwMDAwMDAwMDAwMTEwMTEwMDAwMTEwMTAwMDAwMTAxMSJdLFstNjQsIi0iXSxbLTcwLCItIl0sWy01NSwiMCJdLFstNzQsIjAsMCJdLFstNTgsIi0iXSxbLTE5LCJbMCwwLDAsMCwwLDAsMSwyNCwyNCxcIi1cIiw4MDAsNjAwLDgwMCw2MDAsMSwxLDEzNTAsOTQwLDAsMCwwLDAsXCItXCIsXCItXCIsMTM1MCw5NDAsbnVsbF0iXSxbLTIyLCJbXCJuXCIsXCJuXCJdIl0sWy0yNiwie1widGpoc1wiOjQyMTAwMDAwLFwidWpoc1wiOjE1MjAwMDAwLFwiamhzbFwiOjM3NjAwMDAwMDB9Il0sWy02OSwiTGludXggeDg2XzY0fEdvb2dsZSBJbmMufHw1NnwtfC0iXSxbLTUzLCIwMDEiXSxbLTcxLCJhMDExMDAxMDEwMDEwMDEwMTAwMDEwMTAwMTExMTEwMTAwMDAxMCJdLFstNzIsIkV4VT0iXSxbImRkYiIsIjAsMTEsMCwwLDAsMiwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDEsMCwwLDAsMiwwLDAsMCwwLDAsMSwxLDMsMTYsMCw0LDEsMywwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMSwwLDE1LDAsMCwxLDAsMCwwLDEsMSwwLDAsMCJdLFsiY2IiLCIwLDAsMCwwLDAsMCwwLDAsMSwyLDAsMCwxMSwwLDAsNSwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMSwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMSwwLDEsMSwwLDAsMSwwLDAsMCwwLDEsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDEsMCwwLDAsMCwwLDAsMSwwLDAsMCwwLDAsMCwwLDAsMCwyLDAsMCwwLDEsMCwwLDEiXV0%3D&dep=0&pre=0&sdd=&cri=fqAne8RIw5&pto=2606&ver=65&gac=-&mei=&ap=&fe=1&duid=1.1756150223.YVG3JTEVgf9ywIYO&suid=1.1756150223.4bvPKt14TpOsCR9g&tuid=1.1756150223.xytAvRB2DNsL7K7j&fbc=-&gtm=-&it=7%2C2191%2C60&fbcl=-&gacl=-&gacsd=-&rtic=-&rtict=-&bgc=-&spa=1&urid=0&ab=&sck=-&io=aGA2Og%3D%3D",
                    "mainThreadTime": 25.624,
                    "tbtImpact": 0,
                    "blockingTime": 0,
                    "transferSize": 1686
                  },
                  {
                    "transferSize": 774,
                    "url": "https://obseu.youseasky.com/mon",
                    "tbtImpact": 0,
                    "mainThreadTime": 0,
                    "blockingTime": 0
                  },
                  {
                    "mainThreadTime": 0,
                    "url": "https://obseu.youseasky.com/tracker/tc_imp.gif?e=37dfbd8ee84e00126fe8c630ea4588999225c24f567d43d6da1908be6245cad7bd70a976750ef80ed89373bfe70e9c20c1e53e8d56118a6d2217071a10acf9f29f671f8282d8562c6b1bfd7e21578738de61ce553401279a010456640d59c0b96f4c77be26bb25cb43e2953dee536fae13246410d85afe5aecd2948a7fe07f52a13ad2a24710d14e681f2d1586d31c64e56ad2b785ba130be20ad7bc29917f9e3e9840f85473be5266e97c56052ca4482bc9d8a5e416af3db153bb46a1352837a6d2347e25795f957df2e57d8d7829e8cfe879186a5583d5757f92902f46681b2c5214a68d2a7e7d19a4e44969effaa37fd2b944771e2bb5a5a384eb2ffc82830ff62ac50f662695b7dff6a3268ccea03ed62104c3ac9c2d4c14f5356cad914265bddfaf27dd53ae4fe6d719cb4b9e9e7ec63961918b3bca3bc5c0e2f088eee01136e46af4e7e823436cf897239aab5df402011f94085bd2998c84c0f1c927c16790d0f58e7fae24287ac4682c97859c426788b821e541e6d315d6409e3d0c0b548c6eec439cd0ad3fe0d776870ce08bdbcb7789490435bd1e5a137f433e9fec40b254f2cb892fe7d127fb9d23d989e5bc32cdbee453607584ec4c47deb0491442f8eff63ff36bdeb303b1f224a022b22d870485678bf169995e5eb0bc9874222d7c117c592f4bf3b4d228ab56a54f5c5e3be4a60d838a1267fcb8c3bbbd6edeeee6fa9afbaef2574e3dfe5b87b6596d815f6307ca61596d71f472b36b18c1ebdd7e8d61d23996ad2ecda4109e7b0b3d3d057d1080dde3da3867489c184589cedfbbb2d64e039eb3d061849b36228cc0182e68e790de5327b622855d9d19fd56fd65d8b2778ddc65b492c195e12e1dfdfc2920c72ff29fbab917826d331303956d4352b3a0418bbe52aae2dfc950a9c7f8707d554ee92fb717ee10ebd57b9c20423f403d7879e05f8e833156a72789e38473bbbd4ff80a30d316072bc5facd1818ae27e7847bb1012d014abc3b3283c2ba74d9157ac39719a1c3cfabd1068b210a7144b62e7a0cfec55b05e562f5f4c3319d87b94c4f76a06a3c1a44924642ec9bf20a51cd3733c19d8541d5c6fa921b30b031b9076350ca5231209683555381d4ffc4bdf140b478b464d725dd9d5d87beba393dee8640c298b9aed6aa809826488dfa3704d82d980b985fe7ed37ba8d898c37a08c8bbda71a6786b8a58703b308d7014d3b4c3fd89a6f678026bf10&cri=fqAne8RIw5&ts=224&cb=1756150224129",
                    "tbtImpact": 0,
                    "transferSize": 249,
                    "blockingTime": 0
                  }
                ],
                "type": "subitems"
              }
            },
            {
              "entity": "cloudfront.net",
              "tbtImpact": 0,
              "transferSize": 23835,
              "subItems": {
                "items": [
                  {
                    "url": "http://d38psrni17bvxu.cloudfront.net/fonts/Port_Lligat_Slab/latin.woff2",
                    "tbtImpact": 0,
                    "transferSize": 11993,
                    "mainThreadTime": 0,
                    "blockingTime": 0
                  },
                  {
                    "tbtImpact": 0,
                    "transferSize": 11842,
                    "mainThreadTime": 0,
                    "url": "http://d38psrni17bvxu.cloudfront.net/themes/cleanPeppermintBlack_657d9013/img/arrows.png",
                    "blockingTime": 0
                  }
                ],
                "type": "subitems"
              },
              "mainThreadTime": 0,
              "blockingTime": 0
            },
            {
              "subItems": {
                "items": [
                  {
                    "url": "https://pagead2.googlesyndication.com/bg/qoxIykLQHporMav0XsqS8NtTd2boZuUJaM-UYWb_7aA.js",
                    "blockingTime": 0,
                    "tbtImpact": 0,
                    "transferSize": 21934,
                    "mainThreadTime": 30.080999999999992
                  },
                  {
                    "tbtImpact": 0,
                    "blockingTime": 0,
                    "transferSize": 746,
                    "url": "https://partner.googleadservices.com/gampad/cookie.js?domain=www.se1gym.co.uk&client=dp-teaminternet09_3ph&product=SAS&callback=__sasCookie&cookie_types=v1%2Cv2",
                    "mainThreadTime": 1.0519999999999998
                  }
                ],
                "type": "subitems"
              },
              "transferSize": 22680,
              "entity": "Google/Doubleclick Ads",
              "blockingTime": 0,
              "mainThreadTime": 31.132999999999992,
              "tbtImpact": 0
            },
            {
              "subItems": {
                "type": "subitems",
                "items": [
                  {
                    "tbtImpact": 0,
                    "transferSize": 7852,
                    "mainThreadTime": 10.373999999999995,
                    "url": "https://ep2.adtrafficquality.google/sodar/sodar2.js",
                    "blockingTime": 0
                  },
                  {
                    "blockingTime": 0,
                    "transferSize": 6896,
                    "mainThreadTime": 0,
                    "url": "https://ep1.adtrafficquality.google/getconfig/sodar?sv=200&tid=afs&tv=10&st=env",
                    "tbtImpact": 0
                  },
                  {
                    "mainThreadTime": 5.3629999999999987,
                    "tbtImpact": 0,
                    "blockingTime": 0,
                    "url": "https://ep2.adtrafficquality.google/sodar/sodar2/237/runner.html",
                    "transferSize": 5732
                  },
                  {
                    "blockingTime": 0,
                    "mainThreadTime": 0,
                    "transferSize": 382,
                    "url": "https://ep1.adtrafficquality.google/pagead/sodar?id=sodar2&v=237&t=2&li=afs_10&jk=0LmsaODgE9_r-cAP17iK0Qg&bg=!4OOl46zNAAbD0V7L49E7ADQBe5WfOBu12a6apHAunArmXJ_piUmk7r8CD2KxYXsGFaeoc05-zyQIlMHdOu4kFFakGVYHAgAAAMVSAAAAB2gBB34AE9k91IHfgjjLAz_ntdwV8U98_HgKAXGyDie6Xq-g4bXSzYBGDBdnEyINGYxSpauWSXNTZDkiTP6pMtI9lsyqmf5m35zsPLl70UOAxK2MDNsFY3V0xGbqkTLcWRgTVlLP6Tu2hyWkax6RHOqbX6mEmKzfhcaPXyez5YOmEdAn2EqtaMeOES58w9uLeqbHIz2JdsSXeKCa--qIxpl02fmqX95Gww6rbhr3Ix5PWrBA58LnM-JNYrG92XRHocbU8ldKDidpEL1mS9uu4HHSfnMhjnJTe-dSJE64ohWfoWUiF9THWX1UAEJYcw90nc2mP-DjuWHLfHiiG_Y4lQ7ybtWkMcWsk7iAaCPDjPq4AtoLKuAmTaZ0hYc9jgIDr5jMbZM_s4yqUFMCVMXKAsLYcXgbSE0-Q1Vh9cacXBY6cpnjLHonbYTfLSG74u6TukM4e_dElOTAT2lYmkRVjWDNvazSzNDuSDM5o0jQvodwtIL3eKJJdh8VldYa79Ploh7I9xvtWLYKmBzxFuGZAUNrV4mJvw2wWDbDaSZcowwlUwJGWXwEIHvRuUtzzvcpGyiAqs7x8WwZB8ttD473ZxQ49b5ZI2loa3PclTZr-kNezlZ3iD8Dh3LAU83dIulbf7gkWPelerrQtuhgtvGsixqI_N71A6F9uhq4Z08XwtdGTvvj_Dhb3IBN7SNn92ZqZnsjvN4NkDVdyM_yYW5IUXdiU6VBO8O2mfxTTqL7OVOdsAq9WrFiXDQEcIozkitPASBpXrg4FLX0R0fpuFl-iIs16vXABBp3fe4dMsjJTlULAKTRc_-S22XDhjduzdtYl-MYyXs4Bni-x5qYQ00fu5aT9dfvIMuAm2cg50vbbNFBssQaGCLpcRkvjpOF8HBMht26cBFi9otqsWQm9cdXs6zn8fXYLu3TTw42X25lxir73lPvKy6OGXEZCR3__s2oMrahZA",
                    "tbtImpact": 0
                  },
                  {
                    "mainThreadTime": 0,
                    "url": "https://ep2.adtrafficquality.google/generate_204?VP_7Ww",
                    "transferSize": 152,
                    "blockingTime": 0,
                    "tbtImpact": 0
                  }
                ]
              },
              "transferSize": 21014,
              "blockingTime": 0,
              "entity": "adtrafficquality.google",
              "tbtImpact": 0,
              "mainThreadTime": 15.736999999999995
            },
            {
              "subItems": {
                "items": [
                  {
                    "mainThreadTime": 0,
                    "transferSize": 1070,
                    "blockingTime": 0,
                    "url": "https://afs.googleusercontent.com/ad_icons/standard/publisher_icon_image/search.svg?c=%23ffffff",
                    "tbtImpact": 0
                  },
                  {
                    "blockingTime": 0,
                    "tbtImpact": 0,
                    "url": "https://afs.googleusercontent.com/ad_icons/standard/publisher_icon_image/chevron.svg?c=%23ffffff",
                    "transferSize": 973,
                    "mainThreadTime": 0
                  }
                ],
                "type": "subitems"
              },
              "blockingTime": 0,
              "tbtImpact": 0,
              "entity": "googleusercontent.com",
              "transferSize": 2043,
              "mainThreadTime": 0
            }
          ],
          "isEntityGrouped": true,
          "type": "table",
          "headings": [
            {
              "label": "Third-Party",
              "key": "entity",
              "valueType": "text",
              "subItemsHeading": {
                "key": "url",
                "valueType": "url"
              }
            },
            {
              "key": "transferSize",
              "granularity": 1,
              "subItemsHeading": {
                "key": "transferSize"
              },
              "label": "Transfer Size",
              "valueType": "bytes"
            },
            {
              "subItemsHeading": {
                "key": "blockingTime"
              },
              "label": "Main-Thread Blocking Time",
              "valueType": "ms",
              "granularity": 1,
              "key": "blockingTime"
            }
          ]
        }
      },
      "listitem": {
        "id": "listitem",
        "title": "List items (`<li>`) are contained within `<ul>`, `<ol>` or `<menu>` parent elements",
        "description": "Screen readers require list items (`<li>`) to be contained within a parent `<ul>`, `<ol>` or `<menu>` to be announced properly. [Learn more about proper list structure](https://dequeuniversity.com/rules/axe/4.10/listitem).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "dom-size-insight": {
        "id": "dom-size-insight",
        "title": "Optimize DOM size",
        "description": "A large DOM can increase the duration of style calculations and layout reflows, impacting page responsiveness. A large DOM will also increase memory usage. [Learn how to avoid an excessive DOM size](https://developer.chrome.com/docs/lighthouse/performance/dom-size/).",
        "score": 1,
        "scoreDisplayMode": "numeric",
        "metricSavings": {
          "INP": 0
        },
        "details": {
          "items": [
            {
              "statistic": "Total elements",
              "value": {
                "type": "numeric",
                "value": 42,
                "granularity": 1
              }
            },
            {
              "value": {
                "value": 11,
                "type": "numeric",
                "granularity": 1
              },
              "node": {
                "path": "1,HTML,1,BODY",
                "snippet": "<body id=\"afd\" style=\"visibility: visible;\">",
                "lhId": "page-4-BODY",
                "nodeLabel": "body#afd",
                "type": "node",
                "boundingRect": {
                  "width": 1350,
                  "top": 16,
                  "left": 0,
                  "height": 782,
                  "right": 1350,
                  "bottom": 798
                },
                "selector": "body#afd"
              },
              "statistic": "Most children"
            },
            {
              "node": {
                "lhId": "page-5-IFRAME",
                "snippet": "<iframe frameborder=\"0\" marginwidth=\"0\" marginheight=\"0\" allowtransparency=\"true\" scrolling=\"no\" width=\"100%\" name=\"{&quot;name&quot;:&quot;master-1&quot;,&quot;slave-1-1&quot;:{&quot;clicktrackUrl&quot;:&quot;https://trkpc.net/munin/a…\" id=\"master-1\" src=\"https://syndicatedsearch.goog/afs/ads?adtest=off&amp;psid=5837883959&amp;pcsa=fals…\" allow=\"attribution-reporting\" style=\"visibility: visible; height: 498px; display: block;\">",
                "nodeLabel": "div.wrapper3 > div.tcHolder > div#tc > iframe#master-1",
                "selector": "div.wrapper3 > div.tcHolder > div#tc > iframe#master-1",
                "boundingRect": {
                  "right": 940,
                  "width": 530,
                  "bottom": 627,
                  "height": 498,
                  "left": 410,
                  "top": 129
                },
                "type": "node",
                "path": "1,HTML,1,BODY,2,DIV,3,DIV,0,DIV,6,DIV,0,DIV,0,IFRAME"
              },
              "statistic": "DOM depth",
              "value": {
                "granularity": 1,
                "value": 7,
                "type": "numeric"
              }
            }
          ],
          "debugData": {
            "type": "debugdata",
            "totalElements": 42,
            "maxChildren": 11,
            "maxDepth": 7
          },
          "type": "table",
          "headings": [
            {
              "valueType": "text",
              "key": "statistic",
              "label": "Statistic"
            },
            {
              "label": "Element",
              "valueType": "node",
              "key": "node"
            },
            {
              "label": "Value",
              "valueType": "numeric",
              "key": "value"
            }
          ]
        }
      },
      "use-landmarks": {
        "id": "use-landmarks",
        "title": "HTML5 landmark elements are used to improve navigation",
        "description": "Landmark elements (`<main>`, `<nav>`, etc.) are used to improve the keyboard navigation of the page for assistive technology. [Learn more about landmark elements](https://developer.chrome.com/docs/lighthouse/accessibility/use-landmarks/).",
        "score": null,
        "scoreDisplayMode": "manual"
      },
      "custom-controls-roles": {
        "id": "custom-controls-roles",
        "title": "Custom controls have ARIA roles",
        "description": "Custom interactive controls have appropriate ARIA roles. [Learn how to add roles to custom controls](https://developer.chrome.com/docs/lighthouse/accessibility/custom-control-roles/).",
        "score": null,
        "scoreDisplayMode": "manual"
      },
      "structured-data": {
        "id": "structured-data",
        "title": "Structured data is valid",
        "description": "Run the [Structured Data Testing Tool](https://search.google.com/structured-data/testing-tool/) and the [Structured Data Linter](http://linter.structured-data.org/) to validate structured data. [Learn more about Structured Data](https://developer.chrome.com/docs/lighthouse/seo/structured-data/).",
        "score": null,
        "scoreDisplayMode": "manual"
      },
      "script-treemap-data": {
        "id": "script-treemap-data",
        "title": "Script Treemap Data",
        "description": "Used for treemap app",
        "score": 1,
        "scoreDisplayMode": "informative",
        "details": {
          "type": "treemap-data",
          "nodes": [
            {
              "resourceBytes": 11257,
              "unusedBytes": 335,
              "name": "http://www.se1gym.co.uk/",
              "encodedBytes": 4039,
              "children": [
                {
                  "unusedBytes": 0,
                  "name": "(inline) var tcblock = {…",
                  "resourceBytes": 968
                },
                {
                  "resourceBytes": 9043,
                  "unusedBytes": 335,
                  "name": "(inline) let isAdult=fal…"
                },
                {
                  "resourceBytes": 673,
                  "unusedBytes": 0,
                  "name": "(inline) var ls = functi…"
                },
                {
                  "resourceBytes": 40,
                  "name": "(inline) x(pageOptions, …",
                  "unusedBytes": 0
                },
                {
                  "unusedBytes": 0,
                  "resourceBytes": 483,
                  "name": "(inline) function getLoa…"
                },
                {
                  "unusedBytes": 0,
                  "resourceBytes": 50,
                  "name": "(inline) loadFeed(...get…"
                }
              ]
            },
            {
              "resourceBytes": 117494,
              "name": "https://euob.youseasky.com/sxp/i/224f85302aa2b6ec30aac9a85da2cbf9.js",
              "unusedBytes": 41245,
              "encodedBytes": 43094
            },
            {
              "unusedBytes": 87512,
              "name": "http://www.google.com/adsense/domains/caf.js?abp=1&adsdeli=true",
              "resourceBytes": 158384,
              "encodedBytes": 57677
            },
            {
              "resourceBytes": 378,
              "encodedBytes": 145,
              "name": "https://partner.googleadservices.com/gampad/cookie.js?domain=www.se1gym.co.uk&client=dp-teaminternet09_3ph&product=SAS&callback=__sasCookie&cookie_types=v1%2Cv2",
              "unusedBytes": 0
            },
            {
              "resourceBytes": 11636,
              "unusedBytes": 99,
              "children": [
                {
                  "unusedBytes": 99,
                  "resourceBytes": 11636,
                  "name": "(inline) window.AFS_AD_R…"
                }
              ],
              "name": "https://syndicatedsearch.goog/afs/ads?adtest=off&psid=5837883959&pcsa=false&channel=000001%2Cbucket011%2Cbucket088&client=dp-teaminternet09_3ph&r=m&hl=en&rpbu=http%3A%2F%2Fwww.se1gym.co.uk%2F%3Fts%3DeyJhbGciOiJBMTI4S1ciLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0.NeKCl3434-fhnmpc7JzRjCIdVoTiSfuwVUEP2Yc-gsu0HmXc_vsFTA.6kyd_O5XT-3k6ObkEsqreg.fOjYJ2KQRB3woJ80Rozyk2zFzhL9IPaY7o0LHDPtW1pnYYwwU3Cey0UOleqiaRcI7K3h55qGWt5SDInzQbKeoYJ-RcjosmWtvgh6jfv0ah4_GTjhVamXOaufcI5E5Pv7FGXwmkt1xEO9TNeMVY7ZLZxUax-NhPw96WaiJZ0uWS3NLXuC_EuaYhmZ89c2Vw2mqMUtACT9lo-5nk4KEc47Sm9v115JGjhEmA4C9ipzAIkv1AqLse02jhlhRERJ2v0fbe3m5U3htU-fmk99vA_m1hx0e9-pcTq_CiSeuTPhtOaikysaC5k5LnEEnb01s6Ypk4i7UH7ZvegMUTLWq_8_0Elwy1KmGZFz51nQMFYvyBYAy4REN6bLeEAPvW45JVNfRBFlebEYXifkv9lt_vDqYlkSt7vFLJO8rUEOm7NXsKw-xwHuJaYp2k4urADKZnrFN8dyI04omA0wPaLcMdzI2-LQsUSbVQvDI-iWO-UWT9XkzYu97yNN7X-01fS-pRZWAkqFd_EVVqjBCwVsiinH17tDuoRZwDbxsPbs43DU4qlxXQgyp7giZeuMDKqrsDNDxCTC8fF8TKVR3tFHqurLq-7mZh_g3SE8uKEGIFwVOQREJ_l1V41r70RvpW67Twx-.nn00YuV_rZifffKjlJ4rzQ&type=3&swp=as-drid-2841604693446448&oe=UTF-8&ie=UTF-8&fexp=21404%2C17300002%2C17301437%2C17301439%2C17301442%2C17301548%2C17301266%2C72717108%2C73027842&format=r3%7Cs&nocache=1231756150223801&num=0&output=afd_ads&domain_name=www.se1gym.co.uk&v=3&bsl=8&pac=2&u_his=2&u_tz=-420&dt=1756150223803&u_w=800&u_h=600&biw=1350&bih=940&psw=1350&psh=754&frm=0&uio=--&cont=tc&drt=0&jsid=caf&nfp=1&jsv=796426389&rurl=http%3A%2F%2Fwww.se1gym.co.uk%2F",
              "encodedBytes": 5056
            },
            {
              "unusedBytes": 110867,
              "encodedBytes": 57549,
              "name": "https://syndicatedsearch.goog/adsense/domains/caf.js?pac=2",
              "resourceBytes": 158382
            },
            {
              "unusedBytes": 0,
              "encodedBytes": 1138,
              "resourceBytes": 3689,
              "name": "https://obseu.youseasky.com/ct?id=80705&url=http%3A%2F%2Fwww.se1gym.co.uk%2F&sf=0&tpi=&ch=AdsDeli%20-%20domain%20-%20landingpage&uvid=9c4a9c1eafd7b052958cfc9bf1bd90941639b350&tsf=0&tsfmi=&tsfu=&cb=1756150223905&hl=2&op=0&ag=2731360679&rand=739255181577657701061820315677051408075158159128090655675510012196508605616879696829621662&fs=1350x940&fst=1350x940&np=linux%20x86_64&nv=google%20inc.&ref=&ss=800x600&nc=0&at=&di=W1siZWYiLDkyNDldLFsiYWJuY2giLDIwXSxbLTYsIntcIndcIjpbXCIwXCIsXCJ0Y2Jsb2NrXCIsXCJzZWFyY2hib3hCbG9ja1wiLFwiZ2V0WE1MaHR0cFwiLFwiYWpheFF1ZXJ5XCIsXCJhamF4QmFja2ZpbGxcIixcImxvYWRGZWVkXCIsXCJ4bWxIdHRwXCIsXCJsc1wiLFwiZ2V0TG9hZEZlZWRBcmd1bWVudHNcIixcIl9fY3RjZ19jdF84MDcwNV9leGVjXCJdLFwiblwiOltdLFwiZFwiOltdfSJdLFstNywiLSJdLFstMTIsIm51bGwiXSxbLTE4LCJbMCwwLDAsMV0iXSxbLTQ2LCIwIl0sWy01NywiV0UwWmVFdExXRUFYVkZ3WkVWRk5UVWxLQXhZV1hFeFdXeGRBVmt4S1hGaEtVa0FYV2xaVUZrcEJTUlpRRmdzTERWOEJEQW9KQzFoWUMxc1BYRm9LQ1ZoWVdnQllBUXhkV0F0YVcxOEFGMU5LQXdnRER3a0xEQTBRRlZoTkdVc1pFVkZOVFVsS0F4WVdYRXhXV3hkQVZreEtYRmhLVWtBWFdsWlVGa3BCU1JaUUZnc0xEVjhCREFvSkMxaFlDMXNQWEZvS0NWaFlXZ0JZQVF4ZFdBdGFXMThBRjFOS0F3Z0REd3dNREFBUSJdLFstNjEsIi0iXSxbLTczLCJFaFE9Il0sWy0yNCwiW10iXSxbLTEwLCItIl0sWy0xMywiLSJdLFstMiwiMTIsZWNYRlgxLzdudHZUZGxXN0s3NlNFRUNDRUpCQVJFV3VpZzBsRUlTQmNRUlVGQlFlbWhpQ0NJU3BVcUlJalNPMUlOaUNLOXBpY2tJVDJiYko5NTVkNTc3djkzM3N6Ym5Td0pJUCJdLFstMzIsIjAiXSxbLTQxLCItIl0sWy02MiwiODAiXSxbLTQsIi0iXSxbLTUsIi0iXSxbLTQ0LCIwLDAsMCw1Il0sWy05LCIrIl0sWzEyLCJ7XCJjdHhcIjpcIndlYmdsXCIsXCJ2XCI6XCJnb29nbGUgaW5jLiAoZ29vZ2xlKVwiLFwiclwiOlwiYW5nbGUgKGdvb2dsZSwgdnVsa2FuIDEuMy4wIChzd2lmdHNoYWRlciBkZXZpY2UgKHN1Ynplcm8pICgweDAwMDBjMGRlKSksIHN3aWZ0c2hhZGVyIGRyaXZlcilcIixcInNsdlwiOlwid2ViZ2wgZ2xzbCBlcyAxLjAgKG9wZW5nbCBlcyBnbHNsIGVzIDEuMCBjaHJvbWl1bSlcIixcImd2ZXJcIjpcIndlYmdsIDEuMCAob3BlbmdsIGVzIDIuMCBjaHJvbWl1bSlcIixcImd2ZW5cIjpcIndlYmtpdFwiLFwiYmVuXCI6MTAsXCJ3Z2xcIjoxLFwiZ3JlblwiOlwid2Via2l0IHdlYmdsXCIsXCJzZWZcIjoxOTMwODIwMjc5LFwic2VjXCI6XCJcIn0iXSxbLTUwLCItIl0sWy01MSwiLSJdLFstMzMsIi0iXSxbLTU2LCJsYW5kc2NhcGUtcHJpbWFyeSJdLFstMzYsIltcIjQvM1wiLFwiNC8zXCJdIl0sWy0xNiwiMCJdLFstNDgsIltcIi1cIixcIi1cIixcIi1cIixcIi1cIixcIi1cIl0iXSxbLTQ5LCItIl0sWy0yOCwiZW4tVVMiXSxbLTI5LCItIl0sWy0zMSwiZmFsc2UiXSxbLTM0LCItIl0sWy0xNCwiLSJdLFstMzUsIlsxNzU2MTUwMjIzODQxLDddIl0sWy00MiwiODgzMzk5MDE2Il0sWy02NSwiLSJdLFstNTIsIi0iXSxbLTE1LCItIl0sWy01OSwiZGVuaWVkIl0sWy0zOCwiaSwtMSwtMSwwLDAsMCwwLDAsMCwyMTg2LC0xLDAsLCwyNTQzLDI1NDQiXSxbLTYwLCItIl0sWy0yMSwiLSJdLFstMjMsIisiXSxbLTE3LCI1NiJdLFstNDAsIjMzIl0sWy02MywiMTYiXSxbLTQ1LCI2MjAsMCwwLDAsMCw1NjIsMCwwLDY0OCw1ODMsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCJdLFstMjUsIi0iXSxbLTExLCJ7XCJ0XCI6XCJcIixcIm1cIjpbXCJkZXNjcmlwdGlvblwiXX0iXSxbLTMwLCJbXCJ2XCIsMF0iXSxbLTY4LCItIl0sWy01NCwie1wiaFwiOltcIjMyOTk3Mjg0NTJcIixcIjgyMjgyMzExOVwiLFwiXzNcIixcIjI4NzI4OTkzMjBcIl0sXCJkXCI6W10sXCJiXCI6W1wiXzBcIixcIjI2NDYwMzg4MlwiXSxcInNcIjoxfSJdLFstMSwiLSJdLFstMywiW10iXSxbLTIwLCItIl0sWy00NywiQW1lcmljYS9Mb3NfQW5nZWxlcyxlbi1VUyxsYXRuLGdyZWdvcnkiXSxbLTgsIi0iXSxbLTI3LCJbMCwxMCwwLFwiNGdcIixudWxsXSJdLFstNjYsImdlb2xvY2F0aW9uLGNodWFmdWxsdmVyc2lvbmxpc3QsY3Jvc3NvcmlnaW5pc29sYXRlZCxzY3JlZW53YWtlbG9jayxwdWJsaWNrZXljcmVkZW50aWFsc2dldCxzaGFyZWRzdG9yYWdlc2VsZWN0dXJsLGNodWFhcmNoLGNvbXB1dGVwcmVzc3VyZSxjaHByZWZlcnNyZWR1Y2VkdHJhbnNwYXJlbmN5LGRlZmVycmVkZmV0Y2gsdXNiLGNoc2F2ZWRhdGEscHVibGlja2V5Y3JlZGVudGlhbHNjcmVhdGUsc2hhcmVkc3RvcmFnZSxkZWZlcnJlZGZldGNobWluaW1hbCxydW5hZGF1Y3Rpb24sY2hkb3dubGluayxjaHVhZm9ybWZhY3RvcnMsb3RwY3JlZGVudGlhbHMscGF5bWVudCxjaHVhLGNodWFtb2RlbCxjaGVjdCxhdXRvcGxheSxjYW1lcmEscHJpdmF0ZXN0YXRldG9rZW5pc3N1YW5jZSxhY2NlbGVyb21ldGVyLGNodWFwbGF0Zm9ybXZlcnNpb24saWRsZWRldGVjdGlvbixwcml2YXRlYWdncmVnYXRpb24saW50ZXJlc3Rjb2hvcnQsY2h2aWV3cG9ydGhlaWdodCxjYXB0dXJlZHN1cmZhY2Vjb250cm9sLGxvY2FsZm9udHMsY2h1YXBsYXRmb3JtLG1pZGksY2h1YWZ1bGx2ZXJzaW9uLHhyc3BhdGlhbHRyYWNraW5nLGNsaXBib2FyZHJlYWQsZ2FtZXBhZCxkaXNwbGF5Y2FwdHVyZSxrZXlib2FyZG1hcCxqb2luYWRpbnRlcmVzdGdyb3VwLGNod2lkdGgsY2hwcmVmZXJzcmVkdWNlZG1vdGlvbixicm93c2luZ3RvcGljcyxlbmNyeXB0ZWRtZWRpYSxneXJvc2NvcGUsc2VyaWFsLGNocnR0LGNodWFtb2JpbGUsd2luZG93bWFuYWdlbWVudCx1bmxvYWQsY2hkcHIsY2hwcmVmZXJzY29sb3JzY2hlbWUsY2h1YXdvdzY0LGF0dHJpYnV0aW9ucmVwb3J0aW5nLGZ1bGxzY3JlZW4saWRlbnRpdHljcmVkZW50aWFsc2dldCxwcml2YXRlc3RhdGV0b2tlbnJlZGVtcHRpb24saGlkLGNodWFiaXRuZXNzLHN0b3JhZ2VhY2Nlc3Msc3luY3hocixjaGRldmljZW1lbW9yeSxjaHZpZXdwb3J0d2lkdGgscGljdHVyZWlucGljdHVyZSxtYWduZXRvbWV0ZXIsY2xpcGJvYXJkd3JpdGUsbWljcm9waG9uZSJdLFstNjcsIi0iXSxbImJuY2giLDE3NF0sWy0zNywiLSJdLFstMzksIltcIjIwMDMwMTA3XCIsMCxcIkdlY2tvXCIsXCJOZXRzY2FwZVwiLFwiTW96aWxsYVwiLG51bGwsbnVsbCxmYWxzZSxudWxsLGZhbHNlLG51bGwsMCxmYWxzZSxmYWxzZSxudWxsLDAsZmFsc2UsZmFsc2UsZmFsc2UsdHJ1ZV0iXSxbLTQzLCIwMDAwMDAwMTAwMDAwMDAwMDAwMTEwMTEwMDAwMTEwMTAwMDAwMTAxMSJdLFstNjQsIi0iXSxbLTcwLCItIl0sWy01NSwiMCJdLFstNzQsIjAsMCJdLFstNTgsIi0iXSxbLTE5LCJbMCwwLDAsMCwwLDAsMSwyNCwyNCxcIi1cIiw4MDAsNjAwLDgwMCw2MDAsMSwxLDEzNTAsOTQwLDAsMCwwLDAsXCItXCIsXCItXCIsMTM1MCw5NDAsbnVsbF0iXSxbLTIyLCJbXCJuXCIsXCJuXCJdIl0sWy0yNiwie1widGpoc1wiOjQyMTAwMDAwLFwidWpoc1wiOjE1MjAwMDAwLFwiamhzbFwiOjM3NjAwMDAwMDB9Il0sWy02OSwiTGludXggeDg2XzY0fEdvb2dsZSBJbmMufHw1NnwtfC0iXSxbLTUzLCIwMDEiXSxbLTcxLCJhMDExMDAxMDEwMDEwMDEwMTAwMDEwMTAwMTExMTEwMTAwMDAxMCJdLFstNzIsIkV4VT0iXSxbImRkYiIsIjAsMTEsMCwwLDAsMiwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDEsMCwwLDAsMiwwLDAsMCwwLDAsMSwxLDMsMTYsMCw0LDEsMywwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMSwwLDE1LDAsMCwxLDAsMCwwLDEsMSwwLDAsMCJdLFsiY2IiLCIwLDAsMCwwLDAsMCwwLDAsMSwyLDAsMCwxMSwwLDAsNSwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMSwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDAsMSwwLDEsMSwwLDAsMSwwLDAsMCwwLDEsMCwwLDAsMCwwLDAsMCwwLDAsMCwwLDEsMCwwLDAsMCwwLDAsMSwwLDAsMCwwLDAsMCwwLDAsMCwyLDAsMCwwLDEsMCwwLDEiXV0%3D&dep=0&pre=0&sdd=&cri=fqAne8RIw5&pto=2606&ver=65&gac=-&mei=&ap=&fe=1&duid=1.1756150223.YVG3JTEVgf9ywIYO&suid=1.1756150223.4bvPKt14TpOsCR9g&tuid=1.1756150223.xytAvRB2DNsL7K7j&fbc=-&gtm=-&it=7%2C2191%2C60&fbcl=-&gacl=-&gacsd=-&rtic=-&rtict=-&bgc=-&spa=1&urid=0&ab=&sck=-&io=aGA2Og%3D%3D"
            },
            {
              "resourceBytes": 58415,
              "name": "https://www.google.com/js/bg/Z-SsKYkj_Kr8t4L84tyvkiZZMnLnK5CX23Vh5jPe2Hs.js",
              "encodedBytes": 22171,
              "unusedBytes": 23,
              "children": [
                {
                  "resourceBytes": 58415,
                  "unusedBytes": 23,
                  "name": "/(unmapped)"
                }
              ]
            },
            {
              "resourceBytes": 19990,
              "encodedBytes": 7089,
              "name": "https://ep2.adtrafficquality.google/sodar/sodar2.js",
              "unusedBytes": 9228
            },
            {
              "encodedBytes": 4940,
              "unusedBytes": 6330,
              "children": [
                {
                  "resourceBytes": 13105,
                  "unusedBytes": 6330,
                  "name": "(inline) (function(){'us…"
                }
              ],
              "name": "https://ep2.adtrafficquality.google/sodar/sodar2/237/runner.html",
              "resourceBytes": 13105
            },
            {
              "resourceBytes": 55315,
              "encodedBytes": 21042,
              "name": "https://pagead2.googlesyndication.com/bg/qoxIykLQHporMav0XsqS8NtTd2boZuUJaM-UYWb_7aA.js",
              "unusedBytes": 23,
              "children": [
                {
                  "resourceBytes": 55315,
                  "name": "/(unmapped)",
                  "unusedBytes": 23
                }
              ]
            }
          ]
        }
      },
      "aria-dialog-name": {
        "id": "aria-dialog-name",
        "title": "Elements with `role=\"dialog\"` or `role=\"alertdialog\"` have accessible names.",
        "description": "ARIA dialog elements without accessible names may prevent screen readers users from discerning the purpose of these elements. [Learn how to make ARIA dialog elements more accessible](https://dequeuniversity.com/rules/axe/4.10/aria-dialog-name).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "speed-index": {
        "id": "speed-index",
        "title": "Speed Index",
        "description": "Speed Index shows how quickly the contents of a page are visibly populated. [Learn more about the Speed Index metric](https://developer.chrome.com/docs/lighthouse/performance/speed-index/).",
        "score": 0.72,
        "scoreDisplayMode": "numeric",
        "displayValue": "1.8 s",
        "numericValue": 1758.7611361545994,
        "numericUnit": "millisecond"
      },
      "first-contentful-paint": {
        "id": "first-contentful-paint",
        "title": "First Contentful Paint",
        "description": "First Contentful Paint marks the time at which the first text or image is painted. [Learn more about the First Contentful Paint metric](https://developer.chrome.com/docs/lighthouse/performance/first-contentful-paint/).",
        "score": 1,
        "scoreDisplayMode": "numeric",
        "displayValue": "0.4 s",
        "numericValue": 400.04759362592642,
        "numericUnit": "millisecond"
      },
      "main-thread-tasks": {
        "id": "main-thread-tasks",
        "title": "Tasks",
        "description": "Lists the toplevel main thread tasks that executed during page load.",
        "score": 1,
        "scoreDisplayMode": "informative",
        "details": {
          "items": [
            {
              "duration": 8.995,
              "startTime": 2187.885
            },
            {
              "duration": 207.868,
              "startTime": 2197.237
            },
            {
              "startTime": 2405.115,
              "duration": 7.886
            },
            {
              "startTime": 2416.75,
              "duration": 26.418
            },
            {
              "duration": 5.481,
              "startTime": 2448.38
            },
            {
              "startTime": 2466.021,
              "duration": 12.122
            },
            {
              "startTime": 2478.968,
              "duration": 34.807
            },
            {
              "duration": 11.322,
              "startTime": 2519.286
            },
            {
              "startTime": 2545.418,
              "duration": 26.921
            },
            {
              "duration": 16.43,
              "startTime": 2572.365
            },
            {
              "startTime": 2602.177,
              "duration": 10.572
            },
            {
              "duration": 6.625,
              "startTime": 2628.181
            },
            {
              "startTime": 2663.153,
              "duration": 18.55
            },
            {
              "duration": 117.675,
              "startTime": 2682.552
            },
            {
              "startTime": 2806.7,
              "duration": 9.95
            },
            {
              "startTime": 2822.035,
              "duration": 7.843
            },
            {
              "startTime": 2840.773,
              "duration": 135.885
            },
            {
              "startTime": 2980.52,
              "duration": 5.909
            },
            {
              "duration": 6.103,
              "startTime": 3038.772
            },
            {
              "startTime": 3054.003,
              "duration": 6.57
            },
            {
              "startTime": 3074.284,
              "duration": 30.25
            },
            {
              "startTime": 3104.856,
              "duration": 14.424
            },
            {
              "startTime": 3120.518,
              "duration": 11.654
            },
            {
              "duration": 11.682,
              "startTime": 3136.811
            },
            {
              "startTime": 3153.048,
              "duration": 11.642
            },
            {
              "duration": 14.725,
              "startTime": 3187.419
            },
            {
              "duration": 6.401,
              "startTime": 3207.359
            },
            {
              "startTime": 3237.381,
              "duration": 12.494
            },
            {
              "startTime": 3957.24,
              "duration": 9.309
            }
          ],
          "headings": [
            {
              "granularity": 1,
              "key": "startTime",
              "valueType": "ms",
              "label": "Start Time"
            },
            {
              "key": "duration",
              "label": "End Time",
              "valueType": "ms",
              "granularity": 1
            }
          ],
          "type": "table"
        }
      },
      "aria-meter-name": {
        "id": "aria-meter-name",
        "title": "ARIA `meter` elements have accessible names",
        "description": "When a meter element doesn't have an accessible name, screen readers announce it with a generic name, making it unusable for users who rely on screen readers. [Learn how to name `meter` elements](https://dequeuniversity.com/rules/axe/4.10/aria-meter-name).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "aria-valid-attr-value": {
        "id": "aria-valid-attr-value",
        "title": "`[aria-*]` attributes have valid values",
        "description": "Assistive technologies, like screen readers, can't interpret ARIA attributes with invalid values. [Learn more about valid values for ARIA attributes](https://dequeuniversity.com/rules/axe/4.10/aria-valid-attr-value).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "table-fake-caption": {
        "id": "table-fake-caption",
        "title": "Tables use `<caption>` instead of cells with the `[colspan]` attribute to indicate a caption.",
        "description": "Screen readers have features to make navigating tables easier. Ensuring that tables use the actual caption element instead of cells with the `[colspan]` attribute may improve the experience for screen reader users. [Learn more about captions](https://dequeuniversity.com/rules/axe/4.10/table-fake-caption).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "redirects-http": {
        "id": "redirects-http",
        "title": "Does not redirect HTTP traffic to HTTPS",
        "description": "Make sure that you redirect all HTTP traffic to HTTPS in order to enable secure web features for all your users. [Learn more](https://developer.chrome.com/docs/lighthouse/pwa/redirects-http/).",
        "score": 0,
        "scoreDisplayMode": "binary"
      },
      "network-dependency-tree-insight": {
        "id": "network-dependency-tree-insight",
        "title": "Network dependency tree",
        "description": "[Avoid chaining critical requests](https://developer.chrome.com/docs/lighthouse/performance/critical-request-chains) by reducing the length of chains, reducing the download size of resources, or deferring the download of unnecessary resources to improve page load.",
        "score": 0,
        "scoreDisplayMode": "numeric",
        "metricSavings": {
          "LCP": 0
        },
        "details": {
          "type": "list",
          "items": [
            {
              "value": {
                "longestChain": {
                  "duration": 6432
                },
                "chains": {
                  "2B324D57CB20BDFACF936725E1BD71D4": {
                    "children": {
                      "52.7": {
                        "children": {},
                        "url": "http://www.se1gym.co.uk/munin/a/ls?t=68acb9cf&token=9c4a9c1eafd7b052958cfc9bf1bd90941639b350",
                        "navStartToEndTime": 6432,
                        "isLongest": true,
                        "transferSize": 0
                      },
                      "52.5": {
                        "url": "http://d38psrni17bvxu.cloudfront.net/fonts/Port_Lligat_Slab/latin.woff2",
                        "transferSize": 11993,
                        "children": {},
                        "navStartToEndTime": 2444
                      },
                      "52.4": {
                        "navStartToEndTime": 2404,
                        "children": {},
                        "url": "http://www.se1gym.co.uk/munin/a/tr/browserjs?domain=se1gym.co.uk&toggle=browserjs&uid=MTc1NjE1MDIyMy40NDU0OmU3YWMzYzM2OGJlODZkOTc1ZDY2NjM4ZWFmZTgzZTk3Y2YyYWUyODUxYWIwZTU3YzFlMWE0MDMxMDhmNjdlNGY6NjhhY2I5Y2Y2Y2JmMA%3D%3D",
                        "transferSize": 537
                      }
                    },
                    "url": "http://www.se1gym.co.uk/",
                    "transferSize": 7768,
                    "navStartToEndTime": 2413,
                    "isLongest": true
                  }
                },
                "type": "network-tree"
              },
              "type": "list-section"
            },
            {
              "description": "[preconnect](https://developer.chrome.com/docs/lighthouse/performance/uses-rel-preconnect/) hints help the browser establish a connection earlier in the page load, saving time when the first request for that origin is made. The following are the origins that the page preconnected to.",
              "value": {
                "value": "no origins were preconnected",
                "type": "text"
              },
              "type": "list-section",
              "title": "Preconnected origins"
            },
            {
              "value": {
                "type": "text",
                "value": "No additional origins are good candidates for preconnecting"
              },
              "type": "list-section",
              "description": "Add [preconnect](https://developer.chrome.com/docs/lighthouse/performance/uses-rel-preconnect/) hints to your most important origins, but try to use no more than 4.",
              "title": "Preconnect candidates"
            }
          ]
        }
      },
      "table-duplicate-name": {
        "id": "table-duplicate-name",
        "title": "Tables have different content in the summary attribute and `<caption>`.",
        "description": "The summary attribute should describe the table structure, while `<caption>` should have the onscreen title. Accurate table mark-up helps users of screen readers. [Learn more about summary and caption](https://dequeuniversity.com/rules/axe/4.10/table-duplicate-name).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "input-button-name": {
        "id": "input-button-name",
        "title": "Input buttons have discernible text.",
        "description": "Adding discernable and accessible text to input buttons may help screen reader users understand the purpose of the input button. [Learn more about input buttons](https://dequeuniversity.com/rules/axe/4.10/input-button-name).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "skip-link": {
        "id": "skip-link",
        "title": "Skip links are focusable.",
        "description": "Including a skip link can help users skip to the main content to save time. [Learn more about skip links](https://dequeuniversity.com/rules/axe/4.10/skip-link).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "notification-on-start": {
        "id": "notification-on-start",
        "title": "Avoids requesting the notification permission on page load",
        "description": "Users are mistrustful of or confused by sites that request to send notifications without context. Consider tying the request to user gestures instead. [Learn more about responsibly getting permission for notifications](https://developer.chrome.com/docs/lighthouse/best-practices/notification-on-start/).",
        "score": 1,
        "scoreDisplayMode": "binary",
        "details": {
          "items": [],
          "headings": [
            {
              "label": "Source",
              "valueType": "source-location",
              "key": "source"
            }
          ],
          "type": "table"
        }
      },
      "csp-xss": {
        "id": "csp-xss",
        "title": "Ensure CSP is effective against XSS attacks",
        "description": "A strong Content Security Policy (CSP) significantly reduces the risk of cross-site scripting (XSS) attacks. [Learn how to use a CSP to prevent XSS](https://developer.chrome.com/docs/lighthouse/best-practices/csp-xss/)",
        "score": 1,
        "scoreDisplayMode": "informative",
        "details": {
          "type": "table",
          "items": [
            {
              "description": "No CSP found in enforcement mode",
              "severity": "High"
            }
          ],
          "headings": [
            {
              "label": "Description",
              "subItemsHeading": {
                "key": "description"
              },
              "key": "description",
              "valueType": "text"
            },
            {
              "valueType": "code",
              "label": "Directive",
              "key": "directive",
              "subItemsHeading": {
                "key": "directive"
              }
            },
            {
              "valueType": "text",
              "label": "Severity",
              "key": "severity",
              "subItemsHeading": {
                "key": "severity"
              }
            }
          ]
        }
      },
      "duplicated-javascript-insight": {
        "id": "duplicated-javascript-insight",
        "title": "Duplicated JavaScript",
        "description": "Remove large, duplicate JavaScript modules from bundles to reduce unnecessary bytes consumed by network activity.",
        "score": null,
        "scoreDisplayMode": "notApplicable",
        "details": {
          "type": "table",
          "headings": [
            {
              "key": "source",
              "subItemsHeading": {
                "valueType": "url",
                "key": "url"
              },
              "label": "Source",
              "valueType": "code"
            },
            {
              "valueType": "bytes",
              "granularity": 10,
              "label": "Duplicated bytes",
              "subItemsHeading": {
                "key": "sourceTransferBytes"
              },
              "key": "wastedBytes"
            }
          ],
          "items": []
        }
      },
      "interactive": {
        "id": "interactive",
        "title": "Time to Interactive",
        "description": "Time to Interactive is the amount of time it takes for the page to become fully interactive. [Learn more about the Time to Interactive metric](https://developer.chrome.com/docs/lighthouse/performance/interactive/).",
        "score": 1,
        "scoreDisplayMode": "numeric",
        "displayValue": "1.2 s",
        "numericValue": 1174.357404461522,
        "numericUnit": "millisecond"
      },
      "uses-text-compression": {
        "id": "uses-text-compression",
        "title": "Enable text compression",
        "description": "Text-based resources should be served with compression (gzip, deflate or brotli) to minimize total network bytes. [Learn more about text compression](https://developer.chrome.com/docs/lighthouse/performance/uses-text-compression/).",
        "score": 1,
        "scoreDisplayMode": "metricSavings",
        "metricSavings": {
          "LCP": 0,
          "FCP": 0
        },
        "details": {
          "overallSavingsBytes": 0,
          "sortedBy": [
            "wastedBytes"
          ],
          "headings": [],
          "debugData": {
            "metricSavings": {
              "FCP": 0,
              "LCP": 0
            },
            "type": "debugdata"
          },
          "items": [],
          "overallSavingsMs": 0,
          "type": "opportunity"
        },
        "numericValue": 0,
        "numericUnit": "millisecond"
      },
      "unminified-css": {
        "id": "unminified-css",
        "title": "Minify CSS",
        "description": "Minifying CSS files can reduce network payload sizes. [Learn how to minify CSS](https://developer.chrome.com/docs/lighthouse/performance/unminified-css/).",
        "score": 1,
        "scoreDisplayMode": "metricSavings",
        "metricSavings": {
          "LCP": 0,
          "FCP": 0
        },
        "details": {
          "sortedBy": [
            "wastedBytes"
          ],
          "overallSavingsMs": 0,
          "type": "opportunity",
          "debugData": {
            "metricSavings": {
              "LCP": 0,
              "FCP": 0
            },
            "type": "debugdata"
          },
          "headings": [],
          "items": [],
          "overallSavingsBytes": 0
        },
        "numericValue": 0,
        "numericUnit": "millisecond"
      },
      "legacy-javascript-insight": {
        "id": "legacy-javascript-insight",
        "title": "Legacy JavaScript",
        "description": "Polyfills and transforms enable older browsers to use new JavaScript features. However, many aren't necessary for modern browsers. Consider modifying your JavaScript build process to not transpile [Baseline](https://web.dev/articles/baseline-and-polyfills) features, unless you know you must support older browsers. [Learn why most sites can deploy ES6+ code without transpiling](https://philipwalton.com/articles/the-state-of-es5-on-the-web/)",
        "score": null,
        "scoreDisplayMode": "notApplicable",
        "details": {
          "items": [],
          "headings": [
            {
              "subItemsHeading": {
                "key": "location",
                "valueType": "source-location"
              },
              "label": "URL",
              "valueType": "url",
              "key": "url"
            },
            {
              "key": null,
              "subItemsHeading": {
                "key": "signal"
              },
              "valueType": "code"
            },
            {
              "label": "Wasted bytes",
              "valueType": "bytes",
              "key": "wastedBytes"
            }
          ],
          "type": "table"
        }
      },
      "is-on-https": {
        "id": "is-on-https",
        "title": "Does not use HTTPS",
        "description": "All sites should be protected with HTTPS, even ones that don't handle sensitive data. This includes avoiding [mixed content](https://developers.google.com/web/fundamentals/security/prevent-mixed-content/what-is-mixed-content), where some resources are loaded over HTTP despite the initial request being served over HTTPS. HTTPS prevents intruders from tampering with or passively listening in on the communications between your app and your users, and is a prerequisite for HTTP/2 and many new web platform APIs. [Learn more about HTTPS](https://developer.chrome.com/docs/lighthouse/pwa/is-on-https/).",
        "score": 0,
        "scoreDisplayMode": "binary",
        "displayValue": "7 insecure requests found",
        "details": {
          "items": [
            {
              "resolution": "Allowed",
              "url": "http://www.se1gym.co.uk/"
            },
            {
              "url": "http://www.se1gym.co.uk/munin/a/tr/browserjs?domain=se1gym.co.uk&toggle=browserjs&uid=MTc1NjE1MDIyMy40NDU0OmU3YWMzYzM2OGJlODZkOTc1ZDY2NjM4ZWFmZTgzZTk3Y2YyYWUyODUxYWIwZTU3YzFlMWE0MDMxMDhmNjdlNGY6NjhhY2I5Y2Y2Y2JmMA%3D%3D",
              "resolution": "Allowed"
            },
            {
              "resolution": "Allowed",
              "url": "http://d38psrni17bvxu.cloudfront.net/themes/cleanPeppermintBlack_657d9013/img/arrows.png"
            },
            {
              "resolution": "Allowed",
              "url": "http://d38psrni17bvxu.cloudfront.net/fonts/Port_Lligat_Slab/latin.woff2"
            },
            {
              "resolution": "Allowed",
              "url": "http://www.se1gym.co.uk/munin/a/ls?t=68acb9cf&token=9c4a9c1eafd7b052958cfc9bf1bd90941639b350"
            },
            {
              "resolution": "Allowed",
              "url": "http://www.google.com/adsense/domains/caf.js?abp=1&adsdeli=true"
            },
            {
              "url": "http://www.se1gym.co.uk/munin/a/tr/answercheck/yes?domain=se1gym.co.uk&caf=1&toggle=answercheck&answer=yes&uid=MTc1NjE1MDIyMy40NDU0OmU3YWMzYzM2OGJlODZkOTc1ZDY2NjM4ZWFmZTgzZTk3Y2YyYWUyODUxYWIwZTU3YzFlMWE0MDMxMDhmNjdlNGY6NjhhY2I5Y2Y2Y2JmMA%3D%3D",
              "resolution": "Allowed"
            }
          ],
          "type": "table",
          "headings": [
            {
              "label": "Insecure URL",
              "valueType": "url",
              "key": "url"
            },
            {
              "label": "Request Resolution",
              "key": "resolution",
              "valueType": "text"
            }
          ]
        }
      },
      "aria-required-children": {
        "id": "aria-required-children",
        "title": "Elements with an ARIA `[role]` that require children to contain a specific `[role]` have all required children.",
        "description": "Some ARIA parent roles must contain specific child roles to perform their intended accessibility functions. [Learn more about roles and required children elements](https://dequeuniversity.com/rules/axe/4.10/aria-required-children).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "aria-deprecated-role": {
        "id": "aria-deprecated-role",
        "title": "Deprecated ARIA roles were not used",
        "description": "Deprecated ARIA roles may not be processed correctly by assistive technology. [Learn more about deprecated ARIA roles](https://dequeuniversity.com/rules/axe/4.10/aria-deprecated-role).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "logical-tab-order": {
        "id": "logical-tab-order",
        "title": "The page has a logical tab order",
        "description": "Tabbing through the page follows the visual layout. Users cannot focus elements that are offscreen. [Learn more about logical tab ordering](https://developer.chrome.com/docs/lighthouse/accessibility/logical-tab-order/).",
        "score": null,
        "scoreDisplayMode": "manual"
      },
      "image-size-responsive": {
        "id": "image-size-responsive",
        "title": "Serves images with appropriate resolution",
        "description": "Image natural dimensions should be proportional to the display size and the pixel ratio to maximize image clarity. [Learn how to provide responsive images](https://web.dev/articles/serve-responsive-images).",
        "score": 1,
        "scoreDisplayMode": "binary",
        "details": {
          "headings": [
            {
              "valueType": "node",
              "key": "node"
            },
            {
              "label": "URL",
              "valueType": "url",
              "key": "url"
            },
            {
              "valueType": "text",
              "label": "Displayed size",
              "key": "displayedSize"
            },
            {
              "valueType": "text",
              "label": "Actual size",
              "key": "actualSize"
            },
            {
              "key": "expectedSize",
              "label": "Expected size",
              "valueType": "text"
            }
          ],
          "type": "table",
          "items": []
        }
      },
      "aria-text": {
        "id": "aria-text",
        "title": "Elements with the `role=text` attribute do not have focusable descendents.",
        "description": "Adding `role=text` around a text node split by markup enables VoiceOver to treat it as one phrase, but the element's focusable descendents will not be announced. [Learn more about the `role=text` attribute](https://dequeuniversity.com/rules/axe/4.10/aria-text).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "largest-contentful-paint-element": {
        "id": "largest-contentful-paint-element",
        "title": "Largest Contentful Paint element",
        "description": "This is the largest contentful element painted within the viewport. [Learn more about the Largest Contentful Paint element](https://developer.chrome.com/docs/lighthouse/performance/lighthouse-largest-contentful-paint/)",
        "score": 1,
        "scoreDisplayMode": "informative",
        "displayValue": "510 ms",
        "metricSavings": {
          "LCP": 0
        },
        "details": {
          "items": [
            {
              "headings": [
                {
                  "label": "Element",
                  "valueType": "node",
                  "key": "node"
                }
              ],
              "type": "table",
              "items": [
                {
                  "node": {
                    "lhId": "page-0-DIV",
                    "snippet": "<div class=\"wrapper2\">",
                    "nodeLabel": "\n\n\nse1gym.co.uk",
                    "path": "1,HTML,1,BODY,2,DIV,3,DIV",
                    "type": "node",
                    "selector": "body#afd > div.wrapper1 > div.wrapper2",
                    "boundingRect": {
                      "width": 1350,
                      "right": 1350,
                      "height": 612,
                      "top": 16,
                      "bottom": 628,
                      "left": 0
                    }
                  }
                }
              ]
            },
            {
              "items": [
                {
                  "percent": "24%",
                  "timing": 121,
                  "phase": "TTFB"
                },
                {
                  "timing": 375.16552188337675,
                  "percent": "73%",
                  "phase": "Load Delay"
                },
                {
                  "percent": "1%",
                  "phase": "Load Time",
                  "timing": 6.3784615475556166
                },
                {
                  "timing": 10.294091469808791,
                  "percent": "2%",
                  "phase": "Render Delay"
                }
              ],
              "headings": [
                {
                  "label": "Phase",
                  "valueType": "text",
                  "key": "phase"
                },
                {
                  "key": "percent",
                  "label": "% of LCP",
                  "valueType": "text"
                },
                {
                  "key": "timing",
                  "label": "Timing",
                  "valueType": "ms"
                }
              ],
              "type": "table"
            }
          ],
          "type": "list"
        }
      },
      "robots-txt": {
        "id": "robots-txt",
        "title": "robots.txt is valid",
        "description": "If your robots.txt file is malformed, crawlers may not be able to understand how you want your website to be crawled or indexed. [Learn more about robots.txt](https://developer.chrome.com/docs/lighthouse/seo/invalid-robots-txt/).",
        "score": 1,
        "scoreDisplayMode": "binary",
        "details": {
          "headings": [
            {
              "label": "Line #",
              "key": "index",
              "valueType": "text"
            },
            {
              "label": "Content",
              "key": "line",
              "valueType": "code"
            },
            {
              "key": "message",
              "label": "Error",
              "valueType": "code"
            }
          ],
          "type": "table",
          "items": []
        }
      },
      "frame-title": {
        "id": "frame-title",
        "title": "`<frame>` or `<iframe>` elements do not have a title",
        "description": "Screen reader users rely on frame titles to describe the contents of frames. [Learn more about frame titles](https://dequeuniversity.com/rules/axe/4.10/frame-title).",
        "score": 0,
        "scoreDisplayMode": "binary",
        "details": {
          "items": [
            {
              "node": {
                "boundingRect": {
                  "height": 498,
                  "right": 940,
                  "width": 530,
                  "top": 129,
                  "left": 410,
                  "bottom": 627
                },
                "explanation": "Fix any of the following:\n  Element has an empty title attribute\n  aria-label attribute does not exist or is empty\n  aria-labelledby attribute does not exist, references elements that do not exist or references elements that are empty\n  Element's default semantics were not overridden with role=\"none\" or role=\"presentation\"",
                "selector": "div.wrapper3 > div.tcHolder > div#tc > iframe#master-1",
                "nodeLabel": "div.wrapper3 > div.tcHolder > div#tc > iframe#master-1",
                "type": "node",
                "snippet": "<iframe frameborder=\"0\" marginwidth=\"0\" marginheight=\"0\" allowtransparency=\"true\" scrolling=\"no\" width=\"100%\" name=\"{&quot;name&quot;:&quot;master-1&quot;,&quot;slave-1-1&quot;:{&quot;clicktrackUrl&quot;:&quot;https://trkpc.net/munin/a…\" id=\"master-1\" src=\"https://syndicatedsearch.goog/afs/ads?adtest=off&amp;psid=5837883959&amp;pcsa=fals…\" allow=\"attribution-reporting\" style=\"visibility: visible; height: 498px; display: block;\">",
                "path": "1,HTML,1,BODY,2,DIV,3,DIV,0,DIV,6,DIV,0,DIV,0,IFRAME",
                "lhId": "1-3-IFRAME"
              }
            }
          ],
          "debugData": {
            "impact": "serious",
            "type": "debugdata",
            "tags": [
              "cat.text-alternatives",
              "wcag2a",
              "wcag412",
              "section508",
              "section508.22.i",
              "TTv5",
              "TT12.d",
              "EN-301-549",
              "EN-9.4.1.2"
            ]
          },
          "headings": [
            {
              "label": "Failing Elements",
              "key": "node",
              "subItemsHeading": {
                "valueType": "node",
                "key": "relatedNode"
              },
              "valueType": "node"
            }
          ],
          "type": "table"
        }
      },
      "network-rtt": {
        "id": "network-rtt",
        "title": "Network Round Trip Times",
        "description": "Network round trip times (RTT) have a large impact on performance. If the RTT to an origin is high, it's an indication that servers closer to the user could improve performance. [Learn more about the Round Trip Time](https://hpbn.co/primer-on-latency-and-bandwidth/).",
        "score": 1,
        "scoreDisplayMode": "informative",
        "displayValue": "0 ms",
        "details": {
          "type": "table",
          "sortedBy": [
            "rtt"
          ],
          "headings": [
            {
              "label": "URL",
              "valueType": "text",
              "key": "origin"
            },
            {
              "granularity": 1,
              "valueType": "ms",
              "label": "Time Spent",
              "key": "rtt"
            }
          ],
          "items": [
            {
              "rtt": 3.4199700000000006,
              "origin": "http://www.se1gym.co.uk"
            },
            {
              "rtt": 1.81734,
              "origin": "http://d38psrni17bvxu.cloudfront.net"
            },
            {
              "origin": "https://obseu.youseasky.com",
              "rtt": 1.5758400000000001
            },
            {
              "origin": "https://partner.googleadservices.com",
              "rtt": 0.89999999999999991
            },
            {
              "rtt": 0.89999999999999991,
              "origin": "https://syndicatedsearch.goog"
            },
            {
              "rtt": 0.89999999999999991,
              "origin": "https://afs.googleusercontent.com"
            },
            {
              "rtt": 0.89999999999999991,
              "origin": "https://ep1.adtrafficquality.google"
            },
            {
              "rtt": 0.89999999999999991,
              "origin": "https://ep2.adtrafficquality.google"
            },
            {
              "rtt": 0.0021842256180766542,
              "origin": "https://www.google.com"
            },
            {
              "rtt": 0.0019559210050619008,
              "origin": "https://pagead2.googlesyndication.com"
            },
            {
              "rtt": 0.0010365117740449121,
              "origin": "http://www.google.com"
            },
            {
              "rtt": 0.00093254962941952482,
              "origin": "https://euob.youseasky.com"
            }
          ]
        },
        "numericValue": 3.4199700000000006,
        "numericUnit": "millisecond"
      },
      "valid-lang": {
        "id": "valid-lang",
        "title": "`[lang]` attributes have a valid value",
        "description": "Specifying a valid [BCP 47 language](https://www.w3.org/International/questions/qa-choosing-language-tags#question) on elements helps ensure that text is pronounced correctly by a screen reader. [Learn how to use the `lang` attribute](https://dequeuniversity.com/rules/axe/4.10/valid-lang).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "bypass": {
        "id": "bypass",
        "title": "The page contains a heading, skip link, or landmark region",
        "description": "Adding ways to bypass repetitive content lets keyboard users navigate the page more efficiently. [Learn more about bypass blocks](https://dequeuniversity.com/rules/axe/4.10/bypass).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "http-status-code": {
        "id": "http-status-code",
        "title": "Page has successful HTTP status code",
        "description": "Pages with unsuccessful HTTP status codes may not be indexed properly. [Learn more about HTTP status codes](https://developer.chrome.com/docs/lighthouse/seo/http-status-code/).",
        "score": 1,
        "scoreDisplayMode": "binary"
      },
      "td-headers-attr": {
        "id": "td-headers-attr",
        "title": "Cells in a `<table>` element that use the `[headers]` attribute refer to table cells within the same table.",
        "description": "Screen readers have features to make navigating tables easier. Ensuring `<td>` cells using the `[headers]` attribute only refer to other cells in the same table may improve the experience for screen reader users. [Learn more about the `headers` attribute](https://dequeuniversity.com/rules/axe/4.10/td-headers-attr).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "td-has-header": {
        "id": "td-has-header",
        "title": "`<td>` elements in a large `<table>` have one or more table headers.",
        "description": "Screen readers have features to make navigating tables easier. Ensuring that `<td>` elements in a large table (3 or more cells in width and height) have an associated table header may improve the experience for screen reader users. [Learn more about table headers](https://dequeuniversity.com/rules/axe/4.10/td-has-header).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "font-display-insight": {
        "id": "font-display-insight",
        "title": "Font display",
        "description": "Consider setting [font-display](https://developer.chrome.com/blog/font-display) to swap or optional to ensure text is consistently visible. swap can be further optimized to mitigate layout shifts with [font metric overrides](https://developer.chrome.com/blog/font-fallbacks).",
        "score": 0,
        "scoreDisplayMode": "metricSavings",
        "displayValue": "Est savings of 30 ms",
        "metricSavings": {
          "FCP": 50,
          "INP": 0
        },
        "details": {
          "headings": [
            {
              "label": "URL",
              "valueType": "url",
              "key": "url"
            },
            {
              "valueType": "ms",
              "label": "Est Savings",
              "key": "wastedMs"
            }
          ],
          "items": [
            {
              "url": "http://d38psrni17bvxu.cloudfront.net/fonts/Port_Lligat_Slab/latin.woff2",
              "wastedMs": 30
            }
          ],
          "type": "table"
        }
      },
      "document-title": {
        "id": "document-title",
        "title": "Document has a `<title>` element",
        "description": "The title gives screen reader users an overview of the page, and search engine users rely on it heavily to determine if a page is relevant to their search. [Learn more about document titles](https://dequeuniversity.com/rules/axe/4.10/document-title).",
        "score": 1,
        "scoreDisplayMode": "binary",
        "details": {
          "type": "table",
          "headings": [
            {
              "label": "Failing Elements",
              "subItemsHeading": {
                "key": "relatedNode",
                "valueType": "node"
              },
              "key": "node",
              "valueType": "node"
            }
          ],
          "items": []
        }
      },
      "document-latency-insight": {
        "id": "document-latency-insight",
        "title": "Document request latency",
        "description": "Your first network request is the most important.  Reduce its latency by avoiding redirects, ensuring a fast server response, and enabling text compression.",
        "score": 0,
        "scoreDisplayMode": "metricSavings",
        "displayValue": "Est savings of 2,090 ms",
        "metricSavings": {
          "LCP": 2100,
          "FCP": 2100
        },
        "details": {
          "type": "checklist",
          "items": {
            "usesCompression": {
              "value": true,
              "label": "Applies text compression"
            },
            "noRedirects": {
              "value": true,
              "label": "Avoids redirects"
            },
            "serverResponseIsFast": {
              "value": false,
              "label": "Server responded slowly (observed 2186 ms)"
            }
          },
          "debugData": {
            "wastedBytes": 0,
            "serverResponseTime": 2186,
            "redirectDuration": 0,
            "uncompressedResponseBytes": 0,
            "type": "debugdata"
          }
        }
      },
      "focus-traps": {
        "id": "focus-traps",
        "title": "User focus is not accidentally trapped in a region",
        "description": "A user can tab into and out of any control or region without accidentally trapping their focus. [Learn how to avoid focus traps](https://developer.chrome.com/docs/lighthouse/accessibility/focus-traps/).",
        "score": null,
        "scoreDisplayMode": "manual"
      },
      "cls-culprits-insight": {
        "id": "cls-culprits-insight",
        "title": "Layout shift culprits",
        "description": "Layout shifts occur when elements move absent any user interaction. [Investigate the causes of layout shifts](https://web.dev/articles/optimize-cls), such as elements being added, removed, or their fonts changing as the page loads.",
        "score": 1,
        "scoreDisplayMode": "informative",
        "metricSavings": {
          "CLS": 0
        },
        "details": {
          "items": [
            {
              "headings": [
                {
                  "key": "node",
                  "subItemsHeading": {
                    "key": "extra"
                  },
                  "label": "Element",
                  "valueType": "node"
                },
                {
                  "label": "Layout shift score",
                  "key": "score",
                  "valueType": "numeric",
                  "subItemsHeading": {
                    "valueType": "text",
                    "key": "cause"
                  },
                  "granularity": 0.001
                }
              ],
              "type": "table",
              "items": [
                {
                  "node": {
                    "value": "Total",
                    "type": "text"
                  },
                  "score": 0.0014474920852919878
                },
                {
                  "node": {
                    "boundingRect": {
                      "top": 644,
                      "left": 439,
                      "height": 154,
                      "bottom": 798,
                      "right": 911,
                      "width": 472
                    },
                    "lhId": "page-2-DIV",
                    "nodeLabel": "2025 Copyright | All Rights Reserved.\n\nPrivacy Policy\n\n\n\n",
                    "snippet": "<div class=\"footer\">",
                    "type": "node",
                    "selector": "body#afd > div.wrapper1 > div.footer",
                    "path": "1,HTML,1,BODY,2,DIV,4,DIV"
                  },
                  "score": 0.0014040288357703647
                },
                {
                  "node": {
                    "selector": "div.wrapper1 > div.sale_diagonal_top > a > span",
                    "snippet": "<span>",
                    "lhId": "page-1-SPAN",
                    "boundingRect": {
                      "right": 1323,
                      "width": 107,
                      "bottom": 130,
                      "top": 24,
                      "height": 107,
                      "left": 1217
                    },
                    "path": "1,HTML,1,BODY,2,DIV,2,DIV,0,A,2,SPAN",
                    "nodeLabel": "BUY THIS DOMAIN.",
                    "type": "node"
                  },
                  "subItems": {
                    "items": [
                      {
                        "cause": "Web font",
                        "extra": {
                          "type": "url",
                          "value": "http://d38psrni17bvxu.cloudfront.net/fonts/Port_Lligat_Slab/latin.woff2"
                        }
                      }
                    ],
                    "type": "subitems"
                  },
                  "score": 0.000043463249521623179
                }
              ]
            }
          ],
          "type": "list"
        }
      },
      "tabindex": {
        "id": "tabindex",
        "title": "No element has a `[tabindex]` value greater than 0",
        "description": "A value greater than 0 implies an explicit navigation ordering. Although technically valid, this often creates frustrating experiences for users who rely on assistive technologies. [Learn more about the `tabindex` attribute](https://dequeuniversity.com/rules/axe/4.10/tabindex).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "no-document-write": {
        "id": "no-document-write",
        "title": "Avoid `document.write()`",
        "description": "For users on slow connections, external scripts dynamically injected via `document.write()` can delay page load by tens of seconds. [Learn how to avoid document.write()](https://developer.chrome.com/docs/lighthouse/best-practices/no-document-write/).",
        "score": 0.5,
        "scoreDisplayMode": "metricSavings",
        "details": {
          "type": "table",
          "headings": [
            {
              "valueType": "source-location",
              "key": "source",
              "label": "Source"
            }
          ],
          "items": [
            {
              "source": {
                "type": "source-location",
                "urlProvider": "network",
                "url": "https://syndicatedsearch.goog/adsense/domains/caf.js?pac=2",
                "line": 44,
                "column": 462
              }
            }
          ]
        }
      },
      "aria-command-name": {
        "id": "aria-command-name",
        "title": "`button`, `link`, and `menuitem` elements have accessible names",
        "description": "When an element doesn't have an accessible name, screen readers announce it with a generic name, making it unusable for users who rely on screen readers. [Learn how to make command elements more accessible](https://dequeuniversity.com/rules/axe/4.10/aria-command-name).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "input-image-alt": {
        "id": "input-image-alt",
        "title": "`<input type=\"image\">` elements have `[alt]` text",
        "description": "When an image is being used as an `<input>` button, providing alternative text can help screen reader users understand the purpose of the button. [Learn about input image alt text](https://dequeuniversity.com/rules/axe/4.10/input-image-alt).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "hreflang": {
        "id": "hreflang",
        "title": "Document has a valid `hreflang`",
        "description": "hreflang links tell search engines what version of a page they should list in search results for a given language or region. [Learn more about `hreflang`](https://developer.chrome.com/docs/lighthouse/seo/hreflang/).",
        "score": 1,
        "scoreDisplayMode": "binary",
        "details": {
          "items": [],
          "type": "table",
          "headings": [
            {
              "subItemsHeading": {
                "valueType": "text",
                "key": "reason"
              },
              "valueType": "code",
              "key": "source"
            }
          ]
        }
      },
      "total-blocking-time": {
        "id": "total-blocking-time",
        "title": "Total Blocking Time",
        "description": "Sum of all time periods between FCP and Time to Interactive, when task length exceeded 50ms, expressed in milliseconds. [Learn more about the Total Blocking Time metric](https://developer.chrome.com/docs/lighthouse/performance/lighthouse-total-blocking-time/).",
        "score": 0.91,
        "scoreDisplayMode": "numeric",
        "displayValue": "140 ms",
        "numericValue": 142.79885141532873,
        "numericUnit": "millisecond"
      },
      "aria-progressbar-name": {
        "id": "aria-progressbar-name",
        "title": "ARIA `progressbar` elements have accessible names",
        "description": "When a `progressbar` element doesn't have an accessible name, screen readers announce it with a generic name, making it unusable for users who rely on screen readers. [Learn how to label `progressbar` elements](https://dequeuniversity.com/rules/axe/4.10/aria-progressbar-name).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "managed-focus": {
        "id": "managed-focus",
        "title": "The user's focus is directed to new content added to the page",
        "description": "If new content, such as a dialog, is added to the page, the user's focus is directed to it. [Learn how to direct focus to new content](https://developer.chrome.com/docs/lighthouse/accessibility/managed-focus/).",
        "score": null,
        "scoreDisplayMode": "manual"
      },
      "image-redundant-alt": {
        "id": "image-redundant-alt",
        "title": "Image elements do not have `[alt]` attributes that are redundant text.",
        "description": "Informative elements should aim for short, descriptive alternative text. Alternative text that is exactly the same as the text adjacent to the link or image is potentially confusing for screen reader users, because the text will be read twice. [Learn more about the `alt` attribute](https://dequeuniversity.com/rules/axe/4.10/image-redundant-alt).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "max-potential-fid": {
        "id": "max-potential-fid",
        "title": "Max Potential First Input Delay",
        "description": "The maximum potential First Input Delay that your users could experience is the duration of the longest task. [Learn more about the Maximum Potential First Input Delay metric](https://developer.chrome.com/docs/lighthouse/performance/lighthouse-max-potential-fid/).",
        "score": 0.88,
        "scoreDisplayMode": "numeric",
        "displayValue": "140 ms",
        "numericValue": 136,
        "numericUnit": "millisecond"
      },
      "uses-long-cache-ttl": {
        "id": "uses-long-cache-ttl",
        "title": "Serve static assets with an efficient cache policy",
        "description": "A long cache lifetime can speed up repeat visits to your page. [Learn more about efficient cache policies](https://developer.chrome.com/docs/lighthouse/performance/uses-long-cache-ttl/).",
        "score": 0.5,
        "scoreDisplayMode": "metricSavings",
        "displayValue": "6 resources found",
        "details": {
          "skipSumming": [
            "cacheLifetimeMs"
          ],
          "type": "table",
          "headings": [
            {
              "key": "url",
              "label": "URL",
              "valueType": "url"
            },
            {
              "label": "Cache TTL",
              "displayUnit": "duration",
              "valueType": "ms",
              "key": "cacheLifetimeMs"
            },
            {
              "valueType": "bytes",
              "displayUnit": "kb",
              "granularity": 1,
              "label": "Transfer Size",
              "key": "totalBytes"
            }
          ],
          "summary": {
            "wastedBytes": 47271.725
          },
          "items": [
            {
              "totalBytes": 11993,
              "url": "http://d38psrni17bvxu.cloudfront.net/fonts/Port_Lligat_Slab/latin.woff2",
              "cacheLifetimeMs": 0,
              "cacheHitProbability": 0,
              "wastedBytes": 11993
            },
            {
              "totalBytes": 11842,
              "cacheLifetimeMs": 0,
              "wastedBytes": 11842,
              "url": "http://d38psrni17bvxu.cloudfront.net/themes/cleanPeppermintBlack_657d9013/img/arrows.png",
              "cacheHitProbability": 0
            },
            {
              "totalBytes": 746,
              "wastedBytes": 746,
              "cacheHitProbability": 0,
              "cacheLifetimeMs": 0,
              "url": "https://partner.googleadservices.com/gampad/cookie.js?domain=www.se1gym.co.uk&client=dp-teaminternet09_3ph&product=SAS&callback=__sasCookie&cookie_types=v1%2Cv2"
            },
            {
              "debugData": {
                "max-age": 43200,
                "type": "debugdata"
              },
              "wastedBytes": 21856.5,
              "url": "https://euob.youseasky.com/sxp/i/224f85302aa2b6ec30aac9a85da2cbf9.js",
              "cacheLifetimeMs": 43200000,
              "cacheHitProbability": 0.5,
              "totalBytes": 43713
            },
            {
              "cacheLifetimeMs": 82800000,
              "url": "https://afs.googleusercontent.com/ad_icons/standard/publisher_icon_image/search.svg?c=%23ffffff",
              "debugData": {
                "max-age": 82800,
                "type": "debugdata",
                "public": true
              },
              "totalBytes": 1070,
              "cacheHitProbability": 0.59166666666666667,
              "wastedBytes": 436.91666666666669
            },
            {
              "totalBytes": 973,
              "url": "https://afs.googleusercontent.com/ad_icons/standard/publisher_icon_image/chevron.svg?c=%23ffffff",
              "cacheHitProbability": 0.59166666666666667,
              "cacheLifetimeMs": 82800000,
              "wastedBytes": 397.30833333333334,
              "debugData": {
                "type": "debugdata",
                "public": true,
                "max-age": 82800
              }
            }
          ],
          "sortedBy": [
            "totalBytes"
          ]
        },
        "numericValue": 47271.725,
        "numericUnit": "byte"
      },
      "valid-source-maps": {
        "id": "valid-source-maps",
        "title": "Page has valid source maps",
        "description": "Source maps translate minified code to the original source code. This helps developers debug in production. In addition, Lighthouse is able to provide further insights. Consider deploying source maps to take advantage of these benefits. [Learn more about source maps](https://developer.chrome.com/docs/devtools/javascript/source-maps/).",
        "score": 1,
        "scoreDisplayMode": "binary",
        "details": {
          "type": "table",
          "headings": [
            {
              "subItemsHeading": {
                "key": "error"
              },
              "label": "URL",
              "key": "scriptUrl",
              "valueType": "url"
            },
            {
              "label": "Map URL",
              "key": "sourceMapUrl",
              "valueType": "url"
            }
          ],
          "items": [
            {
              "scriptUrl": "https://www.google.com/js/bg/Z-SsKYkj_Kr8t4L84tyvkiZZMnLnK5CX23Vh5jPe2Hs.js",
              "subItems": {
                "items": [],
                "type": "subitems"
              }
            },
            {
              "scriptUrl": "https://pagead2.googlesyndication.com/bg/qoxIykLQHporMav0XsqS8NtTd2boZuUJaM-UYWb_7aA.js",
              "subItems": {
                "items": [],
                "type": "subitems"
              }
            }
          ]
        }
      },
      "uses-rel-preconnect": {
        "id": "uses-rel-preconnect",
        "title": "Preconnect to required origins",
        "description": "Consider adding `preconnect` or `dns-prefetch` resource hints to establish early connections to important third-party origins. [Learn how to preconnect to required origins](https://developer.chrome.com/docs/lighthouse/performance/uses-rel-preconnect/).",
        "score": 1,
        "scoreDisplayMode": "metricSavings",
        "metricSavings": {
          "LCP": 0,
          "FCP": 0
        },
        "details": {
          "type": "opportunity",
          "overallSavingsMs": 0,
          "headings": [],
          "items": [],
          "sortedBy": [
            "wastedMs"
          ]
        },
        "warnings": [],
        "numericValue": 0,
        "numericUnit": "millisecond"
      },
      "lcp-breakdown-insight": {
        "id": "lcp-breakdown-insight",
        "title": "LCP breakdown",
        "description": "Each [subpart has specific improvement strategies](https://web.dev/articles/optimize-lcp#lcp-breakdown). Ideally, most of the LCP time should be spent on loading the resources, not within delays.",
        "score": 1,
        "scoreDisplayMode": "informative",
        "metricSavings": {
          "LCP": 0
        },
        "details": {
          "items": [
            {
              "items": [
                {
                  "duration": -0.042,
                  "subpart": "timeToFirstByte",
                  "label": "Time to first byte"
                },
                {
                  "subpart": "resourceLoadDelay",
                  "label": "Resource load delay",
                  "duration": 2406.545
                },
                {
                  "subpart": "resourceLoadDuration",
                  "label": "Resource load duration",
                  "duration": 31.502
                },
                {
                  "label": "Element render delay",
                  "duration": 49.94,
                  "subpart": "elementRenderDelay"
                }
              ],
              "headings": [
                {
                  "valueType": "text",
                  "label": "Subpart",
                  "key": "label"
                },
                {
                  "valueType": "ms",
                  "label": "Duration",
                  "key": "duration"
                }
              ],
              "type": "table"
            },
            {
              "boundingRect": {
                "height": 612,
                "top": 16,
                "left": 0,
                "bottom": 628,
                "right": 1350,
                "width": 1350
              },
              "lhId": "page-0-DIV",
              "selector": "body#afd > div.wrapper1 > div.wrapper2",
              "snippet": "<div class=\"wrapper2\">",
              "type": "node",
              "path": "1,HTML,1,BODY,2,DIV,3,DIV",
              "nodeLabel": "\n\n\nse1gym.co.uk"
            }
          ],
          "type": "list"
        }
      },
      "label-content-name-mismatch": {
        "id": "label-content-name-mismatch",
        "title": "Elements with visible text labels have matching accessible names.",
        "description": "Visible text labels that do not match the accessible name can result in a confusing experience for screen reader users. [Learn more about accessible names](https://dequeuniversity.com/rules/axe/4.10/label-content-name-mismatch).",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "image-delivery-insight": {
        "id": "image-delivery-insight",
        "title": "Improve image delivery",
        "description": "Reducing the download time of images can improve the perceived load time of the page and LCP. [Learn more about optimizing image size](https://developer.chrome.com/docs/lighthouse/performance/uses-optimized-images/)",
        "score": null,
        "scoreDisplayMode": "notApplicable"
      },
      "prioritize-lcp-image": {
        "id": "prioritize-lcp-image",
        "title": "Preload Largest Contentful Paint image",
        "description": "If the LCP element is dynamically added to the page, you should preload the image in order to improve LCP. [Learn more about preloading LCP elements](https://web.dev/articles/optimize-lcp#optimize_when_the_resource_is_discovered).",
        "score": 1,
        "scoreDisplayMode": "metricSavings",
        "metricSavings": {
          "LCP": 0
        },
        "details": {
          "headings": [],
          "type": "opportunity",
          "items": [],
          "debugData": {
            "type": "debugdata",
            "initiatorPath": [
              {
                "initiatorType": "parser",
                "url": "http://d38psrni17bvxu.cloudfront.net/themes/cleanPeppermintBlack_657d9013/img/arrows.png"
              },
              {
                "initiatorType": "other",
                "url": "http://www.se1gym.co.uk/"
              }
            ],
            "pathLength": 2
          },
          "overallSavingsMs": 0,
          "sortedBy": [
            "wastedMs"
          ]
        },
        "numericValue": 0,
        "numericUnit": "millisecond"
      }
    },
    "categories": {
      "performance": {
        "id": "performance",
        "title": "Performance",
        "score": 0.95,
        "auditRefs": [
          {
            "id": "first-contentful-paint",
            "weight": 10,
            "group": "metrics",
            "acronym": "FCP"
          },
          {
            "id": "largest-contentful-paint",
            "weight": 25,
            "group": "metrics",
            "acronym": "LCP"
          },
          {
            "id": "total-blocking-time",
            "weight": 30,
            "group": "metrics",
            "acronym": "TBT"
          },
          {
            "id": "cumulative-layout-shift",
            "weight": 25,
            "group": "metrics",
            "acronym": "CLS"
          },
          {
            "id": "speed-index",
            "weight": 10,
            "group": "metrics",
            "acronym": "SI"
          },
          {
            "id": "cache-insight",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "cls-culprits-insight",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "document-latency-insight",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "dom-size-insight",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "duplicated-javascript-insight",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "font-display-insight",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "forced-reflow-insight",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "image-delivery-insight",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "inp-breakdown-insight",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "lcp-breakdown-insight",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "lcp-discovery-insight",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "legacy-javascript-insight",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "network-dependency-tree-insight",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "render-blocking-insight",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "third-parties-insight",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "viewport-insight",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "interactive",
            "weight": 0,
            "group": "hidden",
            "acronym": "TTI"
          },
          {
            "id": "max-potential-fid",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "first-meaningful-paint",
            "weight": 0,
            "group": "hidden",
            "acronym": "FMP"
          },
          {
            "id": "render-blocking-resources",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "uses-responsive-images",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "offscreen-images",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "unminified-css",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "unminified-javascript",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "unused-css-rules",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "unused-javascript",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "uses-optimized-images",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "modern-image-formats",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "uses-text-compression",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "uses-rel-preconnect",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "server-response-time",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "redirects",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "efficient-animated-content",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "duplicated-javascript",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "legacy-javascript",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "prioritize-lcp-image",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "total-byte-weight",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "uses-long-cache-ttl",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "dom-size",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "critical-request-chains",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "user-timings",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "bootup-time",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "mainthread-work-breakdown",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "font-display",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "third-party-summary",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "third-party-facades",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "largest-contentful-paint-element",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "lcp-lazy-loaded",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "layout-shifts",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "uses-passive-event-listeners",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "no-document-write",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "long-tasks",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "non-composited-animations",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "unsized-images",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "viewport",
            "weight": 0,
            "group": "diagnostics"
          },
          {
            "id": "network-requests",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "network-rtt",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "network-server-latency",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "main-thread-tasks",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "diagnostics",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "metrics",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "screenshot-thumbnails",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "final-screenshot",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "script-treemap-data",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "resource-summary",
            "weight": 0,
            "group": "hidden"
          }
        ]
      },
      "accessibility": {
        "id": "accessibility",
        "title": "Accessibility",
        "description": "These checks highlight opportunities to [improve the accessibility of your web app](https://developer.chrome.com/docs/lighthouse/accessibility/). Automatic detection can only detect a subset of issues and does not guarantee the accessibility of your web app, so [manual testing](https://web.dev/articles/how-to-review) is also encouraged.",
        "score": 0.82,
        "manualDescription": "These items address areas which an automated testing tool cannot cover. Learn more in our guide on [conducting an accessibility review](https://web.dev/articles/how-to-review).",
        "auditRefs": [
          {
            "id": "accesskeys",
            "weight": 0,
            "group": "a11y-navigation"
          },
          {
            "id": "aria-allowed-attr",
            "weight": 0,
            "group": "a11y-aria"
          },
          {
            "id": "aria-allowed-role",
            "weight": 0,
            "group": "a11y-aria"
          },
          {
            "id": "aria-command-name",
            "weight": 0,
            "group": "a11y-aria"
          },
          {
            "id": "aria-conditional-attr",
            "weight": 0,
            "group": "a11y-aria"
          },
          {
            "id": "aria-deprecated-role",
            "weight": 0,
            "group": "a11y-aria"
          },
          {
            "id": "aria-dialog-name",
            "weight": 0,
            "group": "a11y-aria"
          },
          {
            "id": "aria-hidden-body",
            "weight": 10,
            "group": "a11y-aria"
          },
          {
            "id": "aria-hidden-focus",
            "weight": 7,
            "group": "a11y-aria"
          },
          {
            "id": "aria-input-field-name",
            "weight": 0,
            "group": "a11y-aria"
          },
          {
            "id": "aria-meter-name",
            "weight": 0,
            "group": "a11y-aria"
          },
          {
            "id": "aria-progressbar-name",
            "weight": 0,
            "group": "a11y-aria"
          },
          {
            "id": "aria-prohibited-attr",
            "weight": 0,
            "group": "a11y-aria"
          },
          {
            "id": "aria-required-attr",
            "weight": 0,
            "group": "a11y-aria"
          },
          {
            "id": "aria-required-children",
            "weight": 0,
            "group": "a11y-aria"
          },
          {
            "id": "aria-required-parent",
            "weight": 0,
            "group": "a11y-aria"
          },
          {
            "id": "aria-roles",
            "weight": 0,
            "group": "a11y-aria"
          },
          {
            "id": "aria-text",
            "weight": 0,
            "group": "a11y-aria"
          },
          {
            "id": "aria-toggle-field-name",
            "weight": 0,
            "group": "a11y-aria"
          },
          {
            "id": "aria-tooltip-name",
            "weight": 0,
            "group": "a11y-aria"
          },
          {
            "id": "aria-treeitem-name",
            "weight": 0,
            "group": "a11y-aria"
          },
          {
            "id": "aria-valid-attr-value",
            "weight": 0,
            "group": "a11y-aria"
          },
          {
            "id": "aria-valid-attr",
            "weight": 0,
            "group": "a11y-aria"
          },
          {
            "id": "button-name",
            "weight": 0,
            "group": "a11y-names-labels"
          },
          {
            "id": "bypass",
            "weight": 0,
            "group": "a11y-navigation"
          },
          {
            "id": "color-contrast",
            "weight": 7,
            "group": "a11y-color-contrast"
          },
          {
            "id": "definition-list",
            "weight": 0,
            "group": "a11y-tables-lists"
          },
          {
            "id": "dlitem",
            "weight": 0,
            "group": "a11y-tables-lists"
          },
          {
            "id": "document-title",
            "weight": 7,
            "group": "a11y-names-labels"
          },
          {
            "id": "duplicate-id-aria",
            "weight": 0,
            "group": "a11y-aria"
          },
          {
            "id": "form-field-multiple-labels",
            "weight": 0,
            "group": "a11y-names-labels"
          },
          {
            "id": "frame-title",
            "weight": 7,
            "group": "a11y-names-labels"
          },
          {
            "id": "heading-order",
            "weight": 3,
            "group": "a11y-navigation"
          },
          {
            "id": "html-has-lang",
            "weight": 7,
            "group": "a11y-language"
          },
          {
            "id": "html-lang-valid",
            "weight": 7,
            "group": "a11y-language"
          },
          {
            "id": "html-xml-lang-mismatch",
            "weight": 0,
            "group": "a11y-language"
          },
          {
            "id": "image-alt",
            "weight": 0,
            "group": "a11y-names-labels"
          },
          {
            "id": "image-redundant-alt",
            "weight": 0,
            "group": "a11y-names-labels"
          },
          {
            "id": "input-button-name",
            "weight": 0,
            "group": "a11y-names-labels"
          },
          {
            "id": "input-image-alt",
            "weight": 0,
            "group": "a11y-names-labels"
          },
          {
            "id": "label",
            "weight": 0,
            "group": "a11y-names-labels"
          },
          {
            "id": "link-in-text-block",
            "weight": 0,
            "group": "a11y-color-contrast"
          },
          {
            "id": "link-name",
            "weight": 7,
            "group": "a11y-names-labels"
          },
          {
            "id": "list",
            "weight": 0,
            "group": "a11y-tables-lists"
          },
          {
            "id": "listitem",
            "weight": 0,
            "group": "a11y-tables-lists"
          },
          {
            "id": "meta-refresh",
            "weight": 0,
            "group": "a11y-best-practices"
          },
          {
            "id": "meta-viewport",
            "weight": 10,
            "group": "a11y-best-practices"
          },
          {
            "id": "object-alt",
            "weight": 0,
            "group": "a11y-names-labels"
          },
          {
            "id": "select-name",
            "weight": 0,
            "group": "a11y-names-labels"
          },
          {
            "id": "skip-link",
            "weight": 0,
            "group": "a11y-names-labels"
          },
          {
            "id": "tabindex",
            "weight": 0,
            "group": "a11y-navigation"
          },
          {
            "id": "table-duplicate-name",
            "weight": 0,
            "group": "a11y-tables-lists"
          },
          {
            "id": "target-size",
            "weight": 7,
            "group": "a11y-best-practices"
          },
          {
            "id": "td-headers-attr",
            "weight": 0,
            "group": "a11y-tables-lists"
          },
          {
            "id": "th-has-data-cells",
            "weight": 0,
            "group": "a11y-tables-lists"
          },
          {
            "id": "valid-lang",
            "weight": 0,
            "group": "a11y-language"
          },
          {
            "id": "video-caption",
            "weight": 0,
            "group": "a11y-audio-video"
          },
          {
            "id": "focusable-controls",
            "weight": 0
          },
          {
            "id": "interactive-element-affordance",
            "weight": 0
          },
          {
            "id": "logical-tab-order",
            "weight": 0
          },
          {
            "id": "visual-order-follows-dom",
            "weight": 0
          },
          {
            "id": "focus-traps",
            "weight": 0
          },
          {
            "id": "managed-focus",
            "weight": 0
          },
          {
            "id": "use-landmarks",
            "weight": 0
          },
          {
            "id": "offscreen-content-hidden",
            "weight": 0
          },
          {
            "id": "custom-controls-labels",
            "weight": 0
          },
          {
            "id": "custom-controls-roles",
            "weight": 0
          },
          {
            "id": "empty-heading",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "identical-links-same-purpose",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "landmark-one-main",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "label-content-name-mismatch",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "table-fake-caption",
            "weight": 0,
            "group": "hidden"
          },
          {
            "id": "td-has-header",
            "weight": 0,
            "group": "hidden"
          }
        ]
      },
      "best-practices": {
        "id": "best-practices",
        "title": "Best Practices",
        "score": 0.57,
        "auditRefs": [
          {
            "id": "is-on-https",
            "weight": 5,
            "group": "best-practices-trust-safety"
          },
          {
            "id": "redirects-http",
            "weight": 1,
            "group": "best-practices-trust-safety"
          },
          {
            "id": "geolocation-on-start",
            "weight": 1,
            "group": "best-practices-trust-safety"
          },
          {
            "id": "notification-on-start",
            "weight": 1,
            "group": "best-practices-trust-safety"
          },
          {
            "id": "csp-xss",
            "weight": 0,
            "group": "best-practices-trust-safety"
          },
          {
            "id": "has-hsts",
            "weight": 0,
            "group": "best-practices-trust-safety"
          },
          {
            "id": "origin-isolation",
            "weight": 0,
            "group": "best-practices-trust-safety"
          },
          {
            "id": "clickjacking-mitigation",
            "weight": 0,
            "group": "best-practices-trust-safety"
          },
          {
            "id": "trusted-types-xss",
            "weight": 0,
            "group": "best-practices-trust-safety"
          },
          {
            "id": "paste-preventing-inputs",
            "weight": 3,
            "group": "best-practices-ux"
          },
          {
            "id": "image-aspect-ratio",
            "weight": 1,
            "group": "best-practices-ux"
          },
          {
            "id": "image-size-responsive",
            "weight": 1,
            "group": "best-practices-ux"
          },
          {
            "id": "viewport",
            "weight": 1,
            "group": "best-practices-ux"
          },
          {
            "id": "font-size",
            "weight": 0,
            "group": "best-practices-ux"
          },
          {
            "id": "doctype",
            "weight": 1,
            "group": "best-practices-browser-compat"
          },
          {
            "id": "charset",
            "weight": 1,
            "group": "best-practices-browser-compat"
          },
          {
            "id": "js-libraries",
            "weight": 0,
            "group": "best-practices-general"
          },
          {
            "id": "deprecations",
            "weight": 5,
            "group": "best-practices-general"
          },
          {
            "id": "third-party-cookies",
            "weight": 5,
            "group": "best-practices-general"
          },
          {
            "id": "errors-in-console",
            "weight": 1,
            "group": "best-practices-general"
          },
          {
            "id": "valid-source-maps",
            "weight": 0,
            "group": "best-practices-general"
          },
          {
            "id": "inspector-issues",
            "weight": 1,
            "group": "best-practices-general"
          }
        ]
      },
      "seo": {
        "id": "seo",
        "title": "SEO",
        "description": "These checks ensure that your page is following basic search engine optimization advice. There are many additional factors Lighthouse does not score here that may affect your search ranking, including performance on [Core Web Vitals](https://web.dev/explore/vitals). [Learn more about Google Search Essentials](https://support.google.com/webmasters/answer/35769).",
        "score": 0.91,
        "manualDescription": "Run these additional validators on your site to check additional SEO best practices.",
        "auditRefs": [
          {
            "id": "is-crawlable",
            "weight": 4.0434782608695654,
            "group": "seo-crawl"
          },
          {
            "id": "document-title",
            "weight": 1,
            "group": "seo-content"
          },
          {
            "id": "meta-description",
            "weight": 1,
            "group": "seo-content"
          },
          {
            "id": "http-status-code",
            "weight": 1,
            "group": "seo-crawl"
          },
          {
            "id": "link-text",
            "weight": 1,
            "group": "seo-content"
          },
          {
            "id": "crawlable-anchors",
            "weight": 1,
            "group": "seo-crawl"
          },
          {
            "id": "robots-txt",
            "weight": 1,
            "group": "seo-crawl"
          },
          {
            "id": "image-alt",
            "weight": 0,
            "group": "seo-content"
          },
          {
            "id": "hreflang",
            "weight": 1,
            "group": "seo-content"
          },
          {
            "id": "canonical",
            "weight": 0,
            "group": "seo-content"
          },
          {
            "id": "structured-data",
            "weight": 0
          }
        ]
      }
    },
    "categoryGroups": {
      "metrics": {
        "title": "Metrics"
      },
      "seo-crawl": {
        "title": "Crawling and Indexing",
        "description": "To appear in search results, crawlers need access to your app."
      },
      "a11y-language": {
        "title": "Internationalization and localization",
        "description": "These are opportunities to improve the interpretation of your content by users in different locales."
      },
      "seo-content": {
        "title": "Content Best Practices",
        "description": "Format your HTML in a way that enables crawlers to better understand your app’s content."
      },
      "best-practices-ux": {
        "title": "User Experience"
      },
      "seo-mobile": {
        "title": "Mobile Friendly",
        "description": "Make sure your pages are mobile friendly so users don’t have to pinch or zoom in order to read the content pages. [Learn how to make pages mobile-friendly](https://developers.google.com/search/mobile-sites/)."
      },
      "best-practices-trust-safety": {
        "title": "Trust and Safety"
      },
      "best-practices-general": {
        "title": "General"
      },
      "a11y-best-practices": {
        "title": "Best practices",
        "description": "These items highlight common accessibility best practices."
      },
      "diagnostics": {
        "title": "Diagnostics",
        "description": "More information about the performance of your application. These numbers don't [directly affect](https://developer.chrome.com/docs/lighthouse/performance/performance-scoring/) the Performance score."
      },
      "a11y-color-contrast": {
        "title": "Contrast",
        "description": "These are opportunities to improve the legibility of your content."
      },
      "a11y-audio-video": {
        "title": "Audio and video",
        "description": "These are opportunities to provide alternative content for audio and video. This may improve the experience for users with hearing or vision impairments."
      },
      "a11y-names-labels": {
        "title": "Names and labels",
        "description": "These are opportunities to improve the semantics of the controls in your application. This may enhance the experience for users of assistive technology, like a screen reader."
      },
      "best-practices-browser-compat": {
        "title": "Browser Compatibility"
      },
      "a11y-navigation": {
        "title": "Navigation",
        "description": "These are opportunities to improve keyboard navigation in your application."
      },
      "a11y-tables-lists": {
        "title": "Tables and lists",
        "description": "These are opportunities to improve the experience of reading tabular or list data using assistive technology, like a screen reader."
      },
      "insights": {
        "title": "Insights",
        "description": "These insights are also available in the Chrome DevTools Performance Panel - [record a trace](https://developer.chrome.com/docs/devtools/performance/reference) to view more detailed information."
      },
      "a11y-aria": {
        "title": "ARIA",
        "description": "These are opportunities to improve the usage of ARIA in your application which may enhance the experience for users of assistive technology, like a screen reader."
      }
    },
    "timing": {
      "total": 16883
    },
    "i18n": {
      "rendererFormattedStrings": {
        "varianceDisclaimer": "Values are estimated and may vary. The [performance score is calculated](https://developer.chrome.com/docs/lighthouse/performance/performance-scoring/) directly from these metrics.",
        "opportunityResourceColumnLabel": "Opportunity",
        "opportunitySavingsColumnLabel": "Estimated Savings",
        "errorMissingAuditInfo": "Report error: no audit information",
        "errorLabel": "Error!",
        "warningHeader": "Warnings: ",
        "passedAuditsGroupTitle": "Passed audits",
        "notApplicableAuditsGroupTitle": "Not applicable",
        "manualAuditsGroupTitle": "Additional items to manually check",
        "toplevelWarningsMessage": "There were issues affecting this run of Lighthouse:",
        "crcLongestDurationLabel": "Maximum critical path latency:",
        "crcInitialNavigation": "Initial Navigation",
        "lsPerformanceCategoryDescription": "[Lighthouse](https://developers.google.com/web/tools/lighthouse/) analysis of the current page on an emulated mobile network. Values are estimated and may vary.",
        "labDataTitle": "Lab Data",
        "warningAuditsGroupTitle": "Passed audits but with warnings",
        "snippetExpandButtonLabel": "Expand snippet",
        "snippetCollapseButtonLabel": "Collapse snippet",
        "thirdPartyResourcesLabel": "Show 3rd-party resources",
        "runtimeDesktopEmulation": "Emulated Desktop",
        "runtimeMobileEmulation": "Emulated Moto G Power",
        "runtimeNoEmulation": "No emulation",
        "runtimeSettingsBenchmark": "Unthrottled CPU/Memory Power",
        "runtimeSettingsCPUThrottling": "CPU throttling",
        "runtimeSettingsDevice": "Device",
        "runtimeSettingsNetworkThrottling": "Network throttling",
        "runtimeSettingsUANetwork": "User agent (network)",
        "runtimeUnknown": "Unknown",
        "dropdownCopyJSON": "Copy JSON",
        "dropdownDarkTheme": "Toggle Dark Theme",
        "dropdownPrintExpanded": "Print Expanded",
        "dropdownPrintSummary": "Print Summary",
        "dropdownSaveGist": "Save as Gist",
        "dropdownSaveHTML": "Save as HTML",
        "dropdownSaveJSON": "Save as JSON",
        "dropdownViewer": "Open in Viewer",
        "footerIssue": "File an issue",
        "throttlingProvided": "Provided by environment",
        "calculatorLink": "See calculator.",
        "runtimeSettingsAxeVersion": "Axe version",
        "viewTreemapLabel": "View Treemap",
        "showRelevantAudits": "Show audits relevant to:"
      }
    },
    "entities": [
      {
        "name": "se1gym.co.uk",
        "isFirstParty": true,
        "isUnrecognized": true,
        "origins": [
          "http://www.se1gym.co.uk"
        ]
      },
      {
        "name": "youseasky.com",
        "isUnrecognized": true,
        "origins": [
          "https://euob.youseasky.com",
          "https://obseu.youseasky.com"
        ]
      },
      {
        "name": "cloudfront.net",
        "isUnrecognized": true,
        "origins": [
          "http://d38psrni17bvxu.cloudfront.net"
        ]
      },
      {
        "name": "Other Google APIs/SDKs",
        "homepage": "https://developers.google.com/apis-explorer/#p/",
        "category": "utility",
        "origins": [
          "http://www.google.com",
          "https://www.google.com"
        ]
      },
      {
        "name": "Google/Doubleclick Ads",
        "homepage": "https://marketingplatform.google.com/about/enterprise/",
        "category": "ad",
        "origins": [
          "https://partner.googleadservices.com",
          "https://pagead2.googlesyndication.com"
        ]
      },
      {
        "name": "syndicatedsearch.goog",
        "isUnrecognized": true,
        "origins": [
          "https://syndicatedsearch.goog"
        ]
      },
      {
        "name": "googleusercontent.com",
        "isUnrecognized": true,
        "origins": [
          "https://afs.googleusercontent.com"
        ]
      },
      {
        "name": "adtrafficquality.google",
        "isUnrecognized": true,
        "origins": [
          "https://ep1.adtrafficquality.google",
          "https://ep2.adtrafficquality.google"
        ]
      }
    ],
    "fullPageScreenshot": {
      "nodes": {
        "page-3-META": {
          "left": 0,
          "bottom": 0,
          "top": 0,
          "right": 0,
          "height": 0,
          "width": 0
        },
        "page-0-DIV": {
          "bottom": 628,
          "left": 0,
          "height": 612,
          "top": 16,
          "width": 1350,
          "right": 1350
        },
        "1-2-A": {
          "height": 15,
          "width": 80,
          "top": 706,
          "right": 715,
          "bottom": 721,
          "left": 635
        },
        "1-3-IFRAME": {
          "right": 940,
          "width": 530,
          "id": "master-1",
          "height": 498,
          "left": 410,
          "top": 129,
          "bottom": 627
        },
        "1-11-META": {
          "width": 0,
          "bottom": 0,
          "right": 0,
          "height": 0,
          "top": 0,
          "left": 0
        },
        "1-6-A": {
          "top": -89,
          "height": 332,
          "right": 1436,
          "width": 332,
          "left": 1104,
          "bottom": 243
        },
        "1-9-META": {
          "height": 0,
          "right": 0,
          "left": 0,
          "width": 0,
          "bottom": 0,
          "top": 0
        },
        "page-1-SPAN": {
          "bottom": 130,
          "width": 107,
          "height": 107,
          "top": 24,
          "left": 1217,
          "right": 1323
        },
        "1-8-DIV": {
          "height": 612,
          "right": 1350,
          "width": 1350,
          "top": 16,
          "left": 0,
          "bottom": 628
        },
        "1-1-BODY": {
          "id": "afd",
          "height": 782,
          "top": 16,
          "right": 1350,
          "width": 1350,
          "left": 0,
          "bottom": 798
        },
        "1-4-HTML": {
          "left": 0,
          "right": 1350,
          "bottom": 814,
          "height": 814,
          "top": 0,
          "width": 1350
        },
        "page-6-IFRAME": {
          "top": 0,
          "width": 0,
          "right": 0,
          "left": 0,
          "bottom": 0,
          "height": 0
        },
        "1-7-A": {
          "width": 54,
          "left": 675,
          "bottom": 38,
          "height": 22,
          "right": 729,
          "top": 16
        },
        "page-5-IFRAME": {
          "height": 498,
          "top": 129,
          "bottom": 627,
          "width": 530,
          "id": "master-1",
          "right": 940,
          "left": 410
        },
        "page-2-DIV": {
          "height": 154,
          "width": 472,
          "top": 644,
          "bottom": 798,
          "right": 911,
          "left": 439
        },
        "1-0-DIV": {
          "height": 154,
          "width": 472,
          "top": 644,
          "left": 439,
          "right": 911,
          "bottom": 798
        },
        "1-10-META": {
          "bottom": 0,
          "top": 0,
          "height": 0,
          "left": 0,
          "right": 0,
          "width": 0
        },
        "page-4-BODY": {
          "left": 0,
          "bottom": 798,
          "width": 1350,
          "height": 782,
          "right": 1350,
          "top": 16,
          "id": "afd"
        },
        "1-5-SPAN": {
          "left": 1217,
          "right": 1323,
          "height": 107,
          "top": 24,
          "width": 107,
          "bottom": 130
        }
      },
      "screenshot": {
        "height": 940,
        "width": 1350,
        "data": "data:image/webp;base64,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"
      }
    }
  },
  "analysisUTCTimestamp": "2025-08-25T19:30:21.203Z"
}

```

### http://www.thethirdspace.com/ FOR Uncavailable Domains
```json
{
  "error": {
    "code": 400,
    "message": "Lighthouse returned error: FAILED_DOCUMENT_REQUEST. Lighthouse was unable to reliably load the page you requested. Make sure you are testing the correct URL and that the server is properly responding to all requests. (Details: net::ERR_TIMED_OUT)",
    "errors": [
      {
        "message": "Lighthouse returned error: FAILED_DOCUMENT_REQUEST. Lighthouse was unable to reliably load the page you requested. Make sure you are testing the correct URL and that the server is properly responding to all requests. (Details: net::ERR_TIMED_OUT)",
        "domain": "lighthouse",
        "reason": "lighthouseUserError"
      }
    ]
  }
}
```