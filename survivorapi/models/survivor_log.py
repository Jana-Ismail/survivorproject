from django.db import models
from django.contrib.auth.models import User

class SurvivorLog(models.Model):
    survivor = models.ForeignKey("Survivor", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    season_log = models.ForeignKey("SeasonLog", on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)
    is_juror = models.BooleanField(default=False)
    episode_voted_out = models.IntegerField(null=True, blank=True)
    is_user_winner_pick = models.BooleanField(default=False)
    is_season_winner = models.BooleanField(default=False)

    @property
    def achievement_stats(self):
        """
        Calculate achievement statistics for this survivor

        Returns:
            dict: Stats for each achievement type including:
                - total_points: Total points across all achievements
                - found_advantages: Points and count for found advantages
                - found_idols: Points and count for found idols
                - played_idols: Points and count for played idols
                - won_team_immunities: Points and count for team immunity wins
                - won_individual_immunities: Points and count for individual immunity wins
                - won_rewards: Points and count for reward wins
        """
        from .found_advantage import FoundAdvantage
        from .found_idol import FoundIdol
        from .played_idol import PlayedIdol
        from .won_immunity import WonImmunity
        from .won_reward import WonReward
        
        advantage_stats = FoundAdvantage.get_stats_for_survivor(self.id)
        idol_stats = FoundIdol.get_stats_for_survivor(self.id)
        played_idol_stats = PlayedIdol.get_stats_for_survivor(self.id)
        immunity_stats = WonImmunity.get_stats_for_survivor(self.id)
        reward_stats = WonReward.get_stats_for_survivor(self.id)

        total_points = (
            advantage_stats['points'] +
            idol_stats['points'] +
            played_idol_stats['points'] +
            immunity_stats['individual']['points'] +
            immunity_stats['team']['points'] +
            reward_stats['points']
        )

        return {
            'total_points': total_points,
            'found_advantages': {
                'points': advantage_stats['points'],
                'count': advantage_stats['count']
            },
            'found_idols': {
                "points": idol_stats['points'],
                "count": idol_stats['count']
            },
            'played_idols': {
                "points": played_idol_stats['points'],
                "count": played_idol_stats['count']
            },
            'won_team_immunities': {
                "points": immunity_stats['team']['points'],
                "count": immunity_stats['team']['count']
            },
            'won_individual_immunities': {
                "points": immunity_stats['individual']['points'],
                "count": immunity_stats['individual']['count']
            },
            'won_rewards': {
                "points": reward_stats['points'],
                "count": reward_stats['count']
            }
        }