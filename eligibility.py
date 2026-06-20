def check_eligibility(income, children, unemployed):

    programs = []

    if income < 2500:
        programs.append("Medicaid")

    if children:
        programs.append("CHIP")

    if unemployed:
        programs.append("ACA Marketplace Subsidy")

    programs.append("Community Health Center")

    return programs