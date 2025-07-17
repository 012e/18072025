from scraper.optiapi.client import OptiSignsClient


async def test_sections():
    """Test the sections API functionality."""
    async with OptiSignsClient() as client:
        # TODO: This is hard coded.
        category_id = 360001365953
        
        print(f"Testing get_sections for category {category_id}...")
        sections_response = await client.get_sections(
            category_id=category_id,
            sort_by="position",
            sort_order="desc",
            per_page=100
        )
        
        print(f"Got {len(sections_response.sections)} sections")
        print(f"Page info: {sections_response.page}/{sections_response.page_count}")
        print(f"Total count: {sections_response.count}")
        
        if sections_response.sections:
            first_section = sections_response.sections[0]
            print(f"First section: {first_section.name} (ID: {first_section.id})")
            print(f"Position: {first_section.position}")
            print(f"Category ID: {first_section.category_id}")
        
        print("\nTesting get_all_sections...")
        all_sections = await client.get_all_sections(
            category_id=category_id,
            sort_by="position",
            sort_order="desc"
        )
        
        total_sections = sum(len(response.sections) for response in all_sections)
        print(f"Got {total_sections} sections across {len(all_sections)} pages")
