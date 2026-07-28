

from collections import defaultdict


class MonitoringSystem:
    def __init__(self):
        self.reported_incidents = []
        self.reports_log = []
        self.incident_count_by_type = defaultdict(int)
        self.incident_count_by_district = defaultdict(int)
        self.decoy_reports = []



    def report_incident(self, incident, reported_by=None, is_decoy=False, city=None, tick=None):

        self.reported_incidents.append(incident)
        self.reports_log.append((incident, reported_by, tick))
        self.incident_count_by_type[incident.incident_type.value] += 1

        if city is not None:
            district = city.get_district_at(*incident.position)
            self.incident_count_by_district[district.name] += 1

        if is_decoy:
            self.decoy_reports.append(incident)

    def get_active_incidents(self):
        return [i for i in self.reported_incidents if not i.resolved]

    def mark_resolved(self, incident, tick=None):
        incident.resolved = True
        incident.time_resolved = tick

    def expire_stale_incidents(self, current_tick, max_age=40):

        expired = 0
        for incident in self.get_active_incidents():
            if incident.time_created is not None and (current_tick - incident.time_created) > max_age:
                incident.resolved = True
                incident.expired = True
                incident.time_resolved = current_tick
                expired += 1
        return expired

    def prioritised_incidents(self):

        active = self.get_active_incidents()
        return sorted(active, key=lambda i: (-i.severity, i.id))



    def basic_statistics(self):

        total = len(self.reported_incidents)
        genuinely_resolved = len([i for i in self.reported_incidents if i.resolved and not i.expired])
        expired = len([i for i in self.reported_incidents if i.expired])
        active = len([i for i in self.reported_incidents if not i.resolved])
        return {
            "total_incidents": total,
            "resolved_incidents": genuinely_resolved,
            "expired_incidents": expired,
            "active_incidents": active,
            "resolution_rate": (genuinely_resolved / total) if total else 0.0,
            "by_type": dict(self.incident_count_by_type),
            "by_district": dict(self.incident_count_by_district),
        }



    def analyse_trends(self):

        stats = self.basic_statistics()
        if not stats["by_district"]:
            return {"hotspot_district": None, "most_common_type": None}

        hotspot = max(stats["by_district"], key=stats["by_district"].get)
        most_common_type = max(stats["by_type"], key=stats["by_type"].get) if stats["by_type"] else None
        return {"hotspot_district": hotspot, "most_common_type": most_common_type}

    def predict_next_hotspot(self):

        recent = self.reported_incidents[-10:]
        if not recent:
            return None

        counts = defaultdict(int)
        for incident in recent:

            counts[incident.incident_type.value] += 1
        return max(counts, key=counts.get)

    def recommend_response(self, spiderman_position, distance_fn):

        active = self.get_active_incidents()
        if not active:
            return None

        def utility(incident):
            distance = distance_fn(incident.position)
            return incident.severity - (0.5 * distance)

        return max(active, key=utility)
