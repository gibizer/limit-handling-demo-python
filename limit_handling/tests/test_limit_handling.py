from limit_handling import model


def test_private_app_limit_is_the_user_limit():
    for plan in [model.FreePlan, model.DeveloperPlan, model.OrganizationPlan]:
        user = model.User(plan)
        app = user.upload_private_app()
        assert app.limit == plan


def test_public_app_has_an_independent_default_limit():
    for plan in [model.FreePlan, model.DeveloperPlan, model.OrganizationPlan]:
        user = model.User(plan=plan)
        app = user.upload_public_app()
        assert app.limit == model.PublicAppPlan


def test_public_app_can_have_custom_limit():
    for plan in [model.FreePlan, model.DeveloperPlan, model.OrganizationPlan]:
        user = model.User(plan)
        app = user.upload_public_app()
        custom_limit = model.Limit(
            concurrent_builds=10,
            max_build_time=75,
            builds_per_month=None,
            max_team_members=None,
        )
        app.limit = custom_limit
        assert app.limit == custom_limit


def test_public_app_can_opt_out_to_get_user_limit():
    for plan in [model.FreePlan, model.DeveloperPlan, model.OrganizationPlan]:
        user = model.User(plan)
        app = user.upload_public_app()
        app.opt_out_from_public_app_limit()
        assert app.limit == plan


def test_public_app_custom_limits_opt_out():
    user = model.User(model.OrganizationPlan)
    app = user.upload_public_app()
    custom_limit = model.Limit(
        concurrent_builds=10,
        max_build_time=75,
        builds_per_month=None,
        max_team_members=None,
    )
    app.limit = custom_limit
    app.opt_out_from_public_app_limit()
    assert app.limit == model.OrganizationPlan
