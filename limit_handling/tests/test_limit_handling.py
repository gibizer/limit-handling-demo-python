import pytest

from limit_handling import model

# single app scenarios


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
        user.opt_out_from_default_public_app_limits(app)
        assert app.limit == plan


def test_private_app_cannot_opt_out():
    user = model.User(model.FreePlan)
    app = user.upload_private_app()
    with pytest.raises(
        TypeError, match="Setting custom limits only allowed for public apps"
    ):
        user.opt_out_from_default_public_app_limits(app)


def test_public_app_custom_limits_opt_out():
    # TODO(gibi): Do we want to allow oping out form custom public app limit?
    # Or only allow opting out if the public app still has the default public
    # app limit?
    pass


def test_demo_scenario():
    free_user = model.User(model.FreePlan)

    free_user_private_app = free_user.upload_private_app()
    assert free_user_private_app.limit == model.FreePlan

    free_user_public_app = free_user.upload_public_app()
    assert free_user_public_app.limit == model.PublicAppPlan

    custom_limit = model.Limit(
        concurrent_builds=10,
        max_build_time=75,
        builds_per_month=None,
        max_team_members=None,
    )
    free_user_public_app.limit = custom_limit
    assert free_user_public_app.limit == custom_limit

    org_user = model.User(model.OrganizationPlan)
    org_user_public_app = free_user.upload_public_app()
    assert org_user_public_app.limit == model.PublicAppPlan

    org_user.opt_out_from_default_public_app_limits(org_user_public_app)
    assert org_user_public_app.limit == model.OrganizationPlan


# multiple app scenarios
