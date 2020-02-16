 # -*- coding: utf-8 -*-
from openfisca_france.model.base import Variable, Individu, MONTH, TypesActivite, select

class tisseo_transport_demandeur_emploi_indemnise_reduction(Variable):
    value_type = float
    entity = Individu
    definition_period = MONTH
    label = u"Pourcentage de la réduction pour les demandeurs d'emploi indemnisés"

    def formula(individu, period, parameters):
        chomage_net = individu('chomage_net', period.last_month)
        indemnise = chomage_net > 0

        smic = parameters(period).cotsoc.gen
        smic_brut_mensuel = smic.smic_h_b * smic.nb_heure_travail_mensuel
        # Utilisation des valeurs indicatives de service-public.fr pour passer du SMIC brut au SMIC net
        # https://www.service-public.fr/particuliers/vosdroits/F2300
        # Dans l'attente de la formule effectivement utilisée par la ville d'Alfortville
        smic_net_mensuel = 7.82 / 9.88 * smic_brut_mensuel

        cmu_c_plafond = individu.famille('cmu_c_plafond', period) / 12
        return indemnise * select([
            chomage_net <= cmu_c_plafond,
            chomage_net <= smic_net_mensuel
            ], [100, 80], default=70)


class tisseo_transport_demandeur_emploi_non_indemnise_reduction(Variable):
    value_type = float
    entity = Individu
    definition_period = MONTH
    label = u"Pourcentage de la réduction pour les demandeurs d'emploi non indemnisés"

    def formula(individu, period, parameters):
        ressources = individu.foyer_fiscal('tisseo_transport_reduction_ressources_fiscales', period.n_2)

        chomeur = individu('activite', period) == TypesActivite.chomeur

        smic = parameters(period).cotsoc.gen
        smic_brut_mensuel = smic.smic_h_b * smic.nb_heure_travail_mensuel
        # Utilisation des valeurs indicatives de service-public.fr pour passer du SMIC brut au SMIC net
        # https://www.service-public.fr/particuliers/vosdroits/F2300
        # Dans l'attente de la formule effectivement utilisée par la ville d'Alfortville
        smic_net_mensuel = 7.82 / 9.88 * smic_brut_mensuel

        return chomeur * (ressources <= smic_net_mensuel) * 80
