    # Get requirements with at least one accepted link for coverage
    covered_reqs_query = (
        select(func.count(func.distinct(RequirementTestCaseLink.requirement_id)))
        .select_from(RequirementTestCaseLink)
        .where(
            RequirementTestCaseLink.link_source.in_([
                LinkSource.MANUAL, LinkSource.AI_CONFIRMED, LinkSource.IMPORTED
            ])
        )
    )
