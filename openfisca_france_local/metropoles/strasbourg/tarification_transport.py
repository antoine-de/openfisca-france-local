from openfisca_france.model.base import (
    Variable,
    Menage,
    Individu,
    Famille,
    MONTH,
    select,
    max_,
)

# TODO: voir comment fusioner ca avec les anciennes regles


class strasbourg_metropole_transport_eligibilite_georaphique(Variable):
    value_type = bool
    entity = Menage
    definition_period = MONTH
    label = "Éligibilité géographique pour la gratuité des transports de l'Eurométropole de Strasbourg"

    def formula(menage, period):
        return menage("menage_dans_epci_siren_246700488", period)


class eurometropole_strasbourg_transport_eligible_carte_emeraude(Variable):
    value_type = bool
    entity = Individu
    definition_period = MONTH
    label = "Éligibilité à la carte emeraude dans les transports de l'Eurométropole de Strasbourg"

    def formula(individu, period):
        """
        Abonnement gratuit sur 6 ans pour les anciens combattants de +
        75 ans résidant dans l'EMS et les veuves de guerre. Trajets
        illimités valables pour une personne
        """
        age = individu("age", period)
        geo = individu.menage(
            "strasbourg_metropole_transport_eligibilite_georaphique", period
        )
        emeraude = individu("ancien_combattant_veuve_de_guerre", period)

        return geo * (age > 75 + emeraude)


class attestion_mdph(Variable):
    # TODO Question: serait-ce l'AEEH ?
    value_type = bool
    entity = Individu
    definition_period = MONTH


# TODO: est-ce un bon nom de champs ?
class ancien_combattant_veuve_de_guerre(Variable):
    # TODO Questoin: serait-ce la même chose que openfisca-france/demography.py:CaseS (ou CaseG ou CaseW) ?
    value_type = bool
    entity = Individu
    definition_period = MONTH


class eurometropole_strasbourg_transport_eligible_gratuite_jeunes_en_situation_handicap(
    Variable
):
    value_type = bool
    entity = Individu
    definition_period = MONTH
    label = "Éligibilité à la gratuité des transports de l'Eurométropole de Strasbourg pour les jeunes en situation de handicap"

    def formula(individu, period):
        """
        Les transports sont gratuits "pour les enfants ayant bénéficié
        d’une prestation de la MDPH et ayant 20 ans ou moins au
        moment de la demande du titre sur présentation d’une
        attestation délivrée par les services de l’EMS à présenter
        en agence CTS."
        """
        age = individu("age", period)
        geo = individu.menage(
            "strasbourg_metropole_transport_eligibilite_georaphique", period
        )
        handicap = individu("attestion_mdph", period)
        return geo * (age <= 20) * handicap


class eurometropole_strasbourg_transport_eligible_gratuite(Variable):
    value_type = bool
    entity = Individu
    definition_period = MONTH
    label = "Éligibilité à la gratuité des transports de l'Eurométropole de Strasbourg"

    def formula(individu, period):
        """
        Les transports sont gratuits pour les mineurs de la métropole,
        les jeunes en situation de handicap
        ou les possesseurs de la carte emeraude
        """
        age = individu("age", period)
        geo = individu.menage(
            "strasbourg_metropole_transport_eligibilite_georaphique", period
        )

        h = individu(
            "eurometropole_strasbourg_transport_eligible_gratuite_jeunes_en_situation_handicap",
            period,
        )
        emeraude = individu(
            "eurometropole_strasbourg_transport_eligible_carte_emeraude", period
        )

        return geo * ((age < 18) + h + emeraude)


class eurometropole_strasbourg_transport_eligible_tarif_reduit(Variable):
    value_type = bool
    entity = Individu
    definition_period = MONTH
    label = (
        "Éligibilité au tarif réduit des transports de l'Eurométropole de Strasbourg"
    )

    def formula(individu, period):
        """
        Les transports sont réduits pour :
        * les moins de 25 ans
        * les personnes avec + de 80% d'invalidité
        * les + de 65 ans
        """
        age = individu("age", period)

        taux_incapacite = individu("taux_incapacite", period)
        pmr = taux_incapacite >= 0.8

        return (age < 25) + pmr + (age >= 65)


class eurometropole_strasbourg_transport_quotient_familial(Variable):
    value_type = float
    entity = Individu
    definition_period = MONTH
    label = "Quotient familial pour la tarification solidaire des transports de l'Eurométropole de Strasbourg"

    def formula(individu, period):
        return (
            individu.foyer_fiscal("rfr", period.n_2)
            / 12
            / individu.foyer_fiscal("nbptr", period.n_2)
        )


class eurometropole_strasbourg_transport_montant_reduit(Variable):
    value_type = float
    entity = Individu
    definition_period = MONTH
    label = "Tarification reduit des transports de l'Eurométropole de Strasbourg"

    def formula(individu, period, parameters):
        qf = individu("eurometropole_strasbourg_transport_quotient_familial", period)
        tarif = parameters(period).metropoles.strasbourg.transport.montant_reduit
        return tarif.calc(max_(0, qf), right=True)


class eurometropole_strasbourg_transport_montant_plein_tarif(Variable):
    value_type = float
    entity = Individu
    definition_period = MONTH
    label = "Tarification 18-25 des transports de l'Eurométropole de Strasbourg"

    def formula(individu, period, parameters):
        qf = individu("eurometropole_strasbourg_transport_quotient_familial", period)
        tarif = parameters(period).metropoles.strasbourg.transport.montant_plein_tarif
        return tarif.calc(max_(0, qf), right=True)


class eurometropole_strasbourg_transport_montant(Variable):
    value_type = float
    entity = Individu
    definition_period = MONTH
    label = "Tarification des transports de l'Eurométropole de Strasbourg"
    reference = [
        "https://www.strasbourg.eu/tarification-solidaire-transports-en-commun"
    ]

    def formula(individu, period):
        gratuit = individu(
            "eurometropole_strasbourg_transport_eligible_gratuite", period
        )
        reduit = individu(
            "eurometropole_strasbourg_transport_eligible_tarif_reduit", period
        )
        age = individu("age", period)

        return select(
            [gratuit, reduit],
            [
                0,
                individu("eurometropole_strasbourg_transport_montant_reduit", period),
            ],
            default=individu(
                "eurometropole_strasbourg_transport_montant_plein_tarif", period
            ),
        )
