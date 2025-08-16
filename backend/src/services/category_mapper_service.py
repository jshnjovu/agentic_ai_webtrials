"""
Category mapping service for translating between Google Places and Yelp category systems.
Provides consistent category mapping for business search across multiple APIs.
"""

from typing import Dict, Any, List
from src.core import BaseService


class CategoryMapperService(BaseService):
    """Service for mapping categories between Google Places and Yelp Fusion APIs."""

    def __init__(self):
        super().__init__("CategoryMapperService")
        self._google_to_yelp_mapping = self._initialize_google_to_yelp_mapping()
        self._yelp_to_google_mapping = self._initialize_yelp_to_google_mapping()

    def _initialize_google_to_yelp_mapping(self) -> Dict[str, List[str]]:
        """Initialize the mapping from Google Places categories to Yelp categories."""
        return {
            # Food & Dining
            "restaurant": ["restaurants", "food"],
            "food": ["restaurants", "food"],
            "cafe": ["cafes", "coffee", "restaurants"],
            "bakery": ["bakeries", "food"],
            "bar": ["bars", "nightlife"],
            "liquor_store": ["beer", "wine", "spirits"],
            # Shopping
            "store": ["shopping"],
            "clothing_store": ["shopping", "fashion"],
            "jewelry_store": ["jewelry", "shopping"],
            "shoe_store": ["shoes", "shopping"],
            "book_store": ["bookstores", "shopping"],
            "electronics_store": ["electronics", "shopping"],
            "hardware_store": ["hardware", "shopping"],
            "convenience_store": ["convenience", "shopping"],
            "department_store": ["departmentstores", "shopping"],
            "supermarket": ["grocery", "shopping"],
            # Health & Beauty
            "beauty_salon": ["beautysvc", "salons"],
            "hair_care": ["beautysvc", "hair"],
            "spa": ["beautysvc", "spas"],
            "dentist": ["health", "dentists"],
            "doctor": ["health", "physicians"],
            "hospital": ["health", "hospitals"],
            "pharmacy": ["health", "pharmacies"],
            "veterinary_care": ["pets", "veterinarians"],
            # Entertainment & Recreation
            "movie_theater": ["arts", "movietheaters"],
            "museum": ["arts", "museums"],
            "park": ["parks", "active"],
            "gym": ["active", "fitness"],
            "bowling_alley": ["active", "bowling"],
            "amusement_park": ["active", "amusementparks"],
            "aquarium": ["active", "aquariums"],
            "zoo": ["active", "zoos"],
            # Professional Services
            "lawyer": ["professional", "attorneys"],
            "accounting": ["professional", "accountants"],
            "real_estate_agency": ["realestate", "agents"],
            "insurance_agency": ["professional", "insurance"],
            "bank": ["financialservices", "banks"],
            "car_dealer": ["automotive", "dealers"],
            "car_rental": ["automotive", "carrental"],
            "car_repair": ["automotive", "autorepair"],
            # Transportation
            "gas_station": ["automotive", "gasstations"],
            "parking": ["automotive", "parking"],
            "taxi_stand": ["transport", "taxis"],
            "bus_station": ["transport", "busstations"],
            "train_station": ["transport", "trainstations"],
            "airport": ["transport", "airports"],
            # Lodging
            "lodging": ["hotels", "travel"],
            "hotel": ["hotels", "travel"],
            "motel": ["hotels", "travel"],
            "campground": ["hotels", "campgrounds"],
            # Education
            "school": ["education", "schools"],
            "university": ["education", "universities"],
            "library": ["education", "libraries"],
            # Religious
            "church": ["religiousorgs", "churches"],
            "mosque": ["religiousorgs", "mosques"],
            "synagogue": ["religiousorgs", "synagogues"],
            "temple": ["religiousorgs", "temples"],
            # Government & Public Services
            "police": ["publicservicesgovt", "police"],
            "fire_station": ["publicservicesgovt", "firestations"],
            "post_office": ["publicservicesgovt", "postoffices"],
            "city_hall": ["publicservicesgovt", "cityhalls"],
            # Other
            "funeral_home": ["localservices", "funeralhomes"],
            "cemetery": ["localservices", "cemeteries"],
            "storage": ["localservices", "selfstorage"],
            "moving_company": ["localservices", "movers"],
            "plumber": ["localservices", "plumbing"],
            "electrician": ["localservices", "electricians"],
            "painter": ["localservices", "painters"],
            "landscaper": ["localservices", "landscaping"],
        }

    def _initialize_yelp_to_google_mapping(self) -> Dict[str, List[str]]:
        """Initialize the mapping from Yelp categories to Google Places categories."""
        return {
            # Food & Dining
            "restaurants": ["restaurant", "food"],
            "food": ["food", "restaurant"],
            "cafes": ["cafe"],
            "coffee": ["cafe"],
            "bakeries": ["bakery"],
            "bars": ["bar"],
            "beer": ["bar", "liquor_store"],
            "wine": ["liquor_store"],
            "spirits": ["liquor_store"],
            # Shopping
            "shopping": ["store"],
            "fashion": ["clothing_store"],
            "jewelry": ["jewelry_store"],
            "shoes": ["shoe_store"],
            "bookstores": ["book_store"],
            "electronics": ["electronics_store"],
            "hardware": ["hardware_store"],
            "convenience": ["convenience_store"],
            "departmentstores": ["department_store"],
            "grocery": ["supermarket"],
            # Health & Beauty
            "beautysvc": ["beauty_salon"],
            "salons": ["beauty_salon"],
            "hair": ["beauty_salon"],
            "spas": ["spa"],
            "health": ["doctor"],
            "dentists": ["dentist"],
            "physicians": ["doctor"],
            "hospitals": ["hospital"],
            "pharmacies": ["pharmacy"],
            "pets": ["veterinary_care"],
            "veterinarians": ["veterinary_care"],
            # Entertainment & Recreation
            "arts": ["museum"],
            "movietheaters": ["movie_theater"],
            "museums": ["museum"],
            "parks": ["park"],
            "active": ["park", "gym"],
            "fitness": ["gym"],
            "bowling": ["bowling_alley"],
            "amusementparks": ["amusement_park"],
            "aquariums": ["aquarium"],
            "zoos": ["zoo"],
            # Professional Services
            "professional": ["lawyer", "accounting"],
            "attorneys": ["lawyer"],
            "accountants": ["accounting"],
            "realestate": ["real_estate_agency"],
            "agents": ["real_estate_agency"],
            "insurance": ["insurance_agency"],
            "financialservices": ["bank"],
            "banks": ["bank"],
            "automotive": ["car_dealer", "car_rental", "car_repair"],
            "dealers": ["car_dealer"],
            "carrental": ["car_rental"],
            "autorepair": ["car_repair"],
            # Transportation
            "gasstations": ["gas_station"],
            "parking": ["parking"],
            "transport": ["taxi_stand", "bus_station", "train_station", "airport"],
            "taxis": ["taxi_stand"],
            "busstations": ["bus_station"],
            "trainstations": ["train_station"],
            "airports": ["airport"],
            # Lodging
            "hotels": ["hotel", "lodging"],
            "travel": ["hotel", "lodging"],
            "motel": ["motel"],
            "campgrounds": ["campground"],
            # Education
            "education": ["school", "university"],
            "schools": ["school"],
            "universities": ["university"],
            "libraries": ["library"],
            # Religious
            "religiousorgs": ["church", "mosque", "synagogue", "temple"],
            "churches": ["church"],
            "mosques": ["mosque"],
            "synagogues": ["synagogue"],
            "temples": ["temple"],
            # Government & Public Services
            "publicservicesgovt": [
                "police",
                "fire_station",
                "post_office",
                "city_hall",
            ],
            "police": ["police"],
            "firestations": ["fire_station"],
            "postoffices": ["post_office"],
            "cityhalls": ["city_hall"],
            # Other
            "localservices": [
                "funeral_home",
                "cemetery",
                "storage",
                "moving_company",
                "plumber",
                "electrician",
                "painter",
                "landscaper",
            ],
            "funeralhomes": ["funeral_home"],
            "cemeteries": ["cemetery"],
            "selfstorage": ["storage"],
            "movers": ["moving_company"],
            "plumbing": ["plumber"],
            "electricians": ["electrician"],
            "painters": ["painter"],
            "landscaping": ["landscaper"],
        }

    def validate_input(self, data: Any) -> bool:
        """Validate input data for the service."""
        return isinstance(data, (str, list)) or data is None

    def map_google_to_yelp(self, google_categories: List[str]) -> List[str]:
        """
        Map Google Places categories to Yelp categories.

        Args:
            google_categories: List of Google Places category strings

        Returns:
            List of corresponding Yelp category strings
        """
        try:
            self.log_operation(
                f"Mapping Google categories to Yelp: {google_categories}"
            )

            if not google_categories:
                return []

            yelp_categories = []
            for google_cat in google_categories:
                if google_cat in self._google_to_yelp_mapping:
                    yelp_categories.extend(self._google_to_yelp_mapping[google_cat])
                else:
                    # Try to find partial matches
                    partial_matches = self._find_partial_matches(
                        google_cat, self._google_to_yelp_mapping.keys()
                    )
                    if partial_matches:
                        yelp_categories.extend(
                            self._google_to_yelp_mapping[partial_matches[0]]
                        )
                    else:
                        # Add generic category if no match found
                        yelp_categories.append(
                            "restaurants"
                            if "food" in google_cat.lower()
                            else "shopping"
                        )

            # Remove duplicates while preserving order
            unique_categories = []
            for cat in yelp_categories:
                if cat not in unique_categories:
                    unique_categories.append(cat)

            self.log_operation(f"Mapped to Yelp categories: {unique_categories}")
            return unique_categories

        except Exception as e:
            self.log_error(e, "map_google_to_yelp")
            return []

    def map_yelp_to_google(self, yelp_categories: List[str]) -> List[str]:
        """
        Map Yelp categories to Google Places categories.

        Args:
            yelp_categories: List of Yelp category strings

        Returns:
            List of corresponding Google Places category strings
        """
        try:
            self.log_operation(f"Mapping Yelp categories to Google: {yelp_categories}")

            if not yelp_categories:
                return []

            google_categories = []
            for yelp_cat in yelp_categories:
                if yelp_cat in self._yelp_to_google_mapping:
                    google_categories.extend(self._yelp_to_google_mapping[yelp_cat])
                else:
                    # Try to find partial matches
                    partial_matches = self._find_partial_matches(
                        yelp_cat, self._yelp_to_google_mapping.keys()
                    )
                    if partial_matches:
                        google_categories.extend(
                            self._yelp_to_google_mapping[partial_matches[0]]
                        )
                    else:
                        # Add generic category if no match found
                        google_categories.append(
                            "store" if "shop" in yelp_cat.lower() else "food"
                        )

            # Remove duplicates while preserving order
            unique_categories = []
            for cat in google_categories:
                if cat not in unique_categories:
                    unique_categories.append(cat)

            self.log_operation(f"Mapped to Google categories: {unique_categories}")
            return unique_categories

        except Exception as e:
            self.log_error(e, "map_yelp_to_google")
            return []

    def _find_partial_matches(
        self, category: str, available_categories: List[str]
    ) -> List[str]:
        """Find partial matches for a category string."""
        category_lower = category.lower()
        matches = []

        for available_cat in available_categories:
            if (
                category_lower in available_cat.lower()
                or available_cat.lower() in category_lower
            ):
                matches.append(available_cat)

        return matches

    def get_mapping_info(self) -> Dict[str, Any]:
        """
        Get information about the category mappings.

        Returns:
            Dictionary with mapping statistics and information
        """
        try:
            google_categories = len(self._google_to_yelp_mapping)
            yelp_categories = len(self._yelp_to_google_mapping)

            # Count total mappings
            total_google_mappings = sum(
                len(categories) for categories in self._google_to_yelp_mapping.values()
            )
            total_yelp_mappings = sum(
                len(categories) for categories in self._yelp_to_google_mapping.values()
            )

            return {
                "google_categories_count": google_categories,
                "yelp_categories_count": yelp_categories,
                "total_google_mappings": total_google_mappings,
                "total_yelp_mappings": total_yelp_mappings,
                "mapping_coverage": {
                    "google_to_yelp": f"{google_categories} categories mapped",
                    "yelp_to_google": f"{yelp_categories} categories mapped",
                },
            }

        except Exception as e:
            self.log_error(e, "get_mapping_info")
            return {"error": str(e)}

    def validate_category_mapping(
        self,
        source_categories: List[str],
        target_categories: List[str],
        source_type: str = "google",
    ) -> Dict[str, Any]:
        """
        Validate the quality of a category mapping.

        Args:
            source_categories: Original source categories
            target_categories: Mapped target categories
            source_type: Type of source ("google" or "yelp")

        Returns:
            Dictionary with validation results
        """
        try:
            if source_type.lower() == "google":
                expected_target = self.map_google_to_yelp(source_categories)
            else:
                expected_target = self.map_yelp_to_google(source_categories)

            # Calculate mapping accuracy
            if not expected_target:
                accuracy = 0.0
            else:
                matches = len(set(target_categories) & set(expected_target))
                accuracy = (
                    (matches / len(expected_target)) * 100 if expected_target else 0.0
                )

            # Check for missing categories
            missing_categories = set(expected_target) - set(target_categories)
            extra_categories = set(target_categories) - set(expected_target)

            return {
                "accuracy_percentage": round(accuracy, 2),
                "source_categories": source_categories,
                "target_categories": target_categories,
                "expected_target": expected_target,
                "missing_categories": list(missing_categories),
                "extra_categories": list(extra_categories),
                "validation_score": (
                    "good" if accuracy >= 80 else "fair" if accuracy >= 60 else "poor"
                ),
            }

        except Exception as e:
            self.log_error(e, "validate_category_mapping")
            return {"error": str(e)}
