from scraper.optiapi.client import OptiSignsClient

async def test_categories():
    """Test the categories API functionality."""
    async with OptiSignsClient() as client:
        print("Testing get_categories...")
        categories_response = await client.get_categories(
            sort_by="position",
            sort_order="asc",
            per_page=50
        )
        
        print(f"Got {len(categories_response.categories)} categories")
        print(f"Page info: {categories_response.page}/{categories_response.page_count}")
        print(f"Total count: {categories_response.count}")
        
        if categories_response.categories:
            first_category = categories_response.categories[0]
            print(f"First category: {first_category.name} (ID: {first_category.id})")
            print(f"Position: {first_category.position}")
            print(f"Description: {first_category.description[:100]}..." if first_category.description else "No description")
        
        print("\nTesting get_all_categories...")
        all_categories = await client.get_all_categories(
            sort_by="position",
            sort_order="asc"
        )
        
        total_categories = sum(len(response.categories) for response in all_categories)
        print(f"Got {total_categories} categories across {len(all_categories)} pages")
        
        # Return the first category ID for use in sections test
        if categories_response.categories:
            return categories_response.categories[0].id
        return None


