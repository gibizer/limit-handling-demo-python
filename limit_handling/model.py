class Limit:
    def __init__(
        self,
        concurrent_builds,
        max_build_time,
        builds_per_month,
        max_team_members,
    ):
        """Represents quotas in the CI system

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


class App:
    def __init__(self, limit):
        self._limit = limit

    @property
    def limit(self):
        return self._limit

    # NOTE(gibi): We could simply delete this and handle the AttributeError in
    # the presentation layer instead
    @limit.setter
    def limit(self, custom_limit):
        raise TypeError("Setting custom limits only allowed for public apps")


class PrivateApp(App):
    def __init__(self, limit):
        super().__init__(limit)


class PublicApp(App):
    def __init__(self):
        super().__init__(PublicAppPlan)

    @App.limit.setter
    def limit(self, custom_limit):
        # TODO(gibi): this operation needs escalated privileges (e.g. admin)
        # as the owner of the app cannot set the its own app limits
        self._limit = custom_limit


class User:
    def __init__(self, plan):
        self.plan = plan

    def upload_private_app(self):
        # TODO(gibi): associate app to the user
        return PrivateApp(limit=self.plan)

    def upload_public_app(self):
        # TODO(gibi): associate app to the user
        return PublicApp()

    def opt_out_from_default_public_app_limits(self, public_app):
        # TODO(gibi): check does the owned by the user
        # TODO(gibi): check does the app public
        public_app.limit = self.plan
