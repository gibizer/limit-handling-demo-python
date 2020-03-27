class Limit:
    """Represents build limits in the CI system."""

    def __init__(
        self,
        concurrent_builds,
        max_build_time,
        builds_per_month,
        max_team_members,
    ):
        """Constructs a limit

        :param concurrent_builds: Maximum number of concurrent builds
        :param max_build_time: Maximum number of minutes any build can take
        :param builds_per_month: Maximum number of builds per months, or None
            if unlimited
        :param max_team_members: Maximum number of accounts, or None if
            unlimited
        """
        self.concurrent_builds = concurrent_builds
        self.max_build_time = max_build_time
        self.builds_per_month = builds_per_month
        self.max_team_members = max_team_members


# NOTE(gibi): These pre-defined limits are hardcoded now but I would put them
# in the DB (out of scope) so eventually they can be changed via an admin API.
FreePlan = Limit(
    concurrent_builds=1,
    max_build_time=10,
    builds_per_month=200,
    max_team_members=2,
)

DeveloperPlan = Limit(
    concurrent_builds=2,
    max_build_time=45,
    builds_per_month=None,
    max_team_members=None,
)

OrganizationPlan = Limit(
    concurrent_builds=4,
    max_build_time=90,
    builds_per_month=None,
    max_team_members=None,
)

PublicAppPlan = Limit(
    concurrent_builds=2,
    max_build_time=45,
    builds_per_month=None,
    max_team_members=None,
)


# NOTE(gibi): Having a base class for now is a bit forced as there is really
# only a small amount of common code to be shared between PrivateApp and
# PublicApp. We could simply go whit two independent classes or even with a
# PublicApp(PrivateApp) inheritance as well.
# However most likely apps will have a lot of code in common in a real life
# scenario.
class App:
    """Represents a buildable application"""

    def __init__(self, owner):
        """ Constructs an App

        This is not intended for direct instantiation. Use the derived
        PrivateApp or PublicApp instead.

        :param owner: The user uploaded the app
        """
        self._owner = owner


class PrivateApp(App):
    """Represents a private app"""

    @property
    def limit(self):
        """The build limits that applies to this app

        A private app inherits its limits from its owner.
        """
        return self._owner.plan


class PublicApp(App):
    """Represents a public app"""

    def __init__(self, owner):
        super().__init__(owner)
        self._limit = None

    @property
    def limit(self):
        """The build limits that applies to this app

        A public app has its own default limit but this limit is
        customizable.
        """
        if self._limit:
            return self._limit
        else:  # no custom limit, go with the default
            return PublicAppPlan

    @limit.setter
    def limit(self, custom_limit):
        """ Customize the limit of the app

        :param custom_limit: The new limit for this app
        """
        # NOTE(gibi): this operation needs escalated privileges (e.g. admin)
        # as the owner of the app cannot set its own app's limits. But
        # authorization is out of scope.
        self._limit = custom_limit

    def opt_out_from_public_app_limit(self):
        # NOTE(gibi): As per clarified requirement it is allowed to opt out
        # from the public app limit even if such limit is already customized.
        # NOTE(gibi): we are reusing the limit customization possibility
        # internally to implement opting out as opting out is basically
        # applying a custom limit based on the owner's plan. The real
        # difference is that the user can only opt out to apply its own plan
        # to the app but the admin can customize the app's limit freely to any
        # plan.
        self._limit = self._owner.plan


class User:
    """Represents the user of a build system

    Each user has a plan associated that describe how much build such user can
    execute. See Limit for the details of such plan.

    """

    def __init__(self, plan):
        """ Constructs a user with a plan

        :param plan: a Limit instance describing how much build a user can
        execute
        """
        self.plan = plan

    def upload_private_app(self):
        """ Create a new private app for the user.

        :return: The PrivateApp instance created
        """
        # NOTE(gibi): Listing apps for a user is out of scope so an app ref is
        # not stored in the user now. In a list-app-by-user scenario it might
        # be beneficial to have a bidirectional link between App and User.
        return PrivateApp(owner=self)

    def upload_public_app(self):
        """ Create a new public app for the user.

        :return: The PublicApp instance created
        """
        # NOTE(gibi): Listing apps for a user is out of scope so an app ref is
        # not stored in the user now. In a list-app-by-user scenario it might
        # be beneficial to have a bidirectional link between App and User.
        return PublicApp(owner=self)

    # NOTE(gibi): we might consider adding an opt_out helper here depending on
    # the needs of the presentation layer that would call
    # app.opt_out_from_public_app_limit() on public apps and raise an error on
    # private apps.
