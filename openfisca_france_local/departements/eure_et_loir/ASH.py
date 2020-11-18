# -*- coding: utf-8 -*-
from openfisca_france.model.base import Variable, Individu, Menage, MONTH

class eure_et_loir_ASH_personne_agee(Variable):
    value_type = bool
    entity = Individu
    definition_period = MONTH
    label = "Éligibilité d'une personne agée à l'aide sociale à l'hébergement en établisement"
    reference = """Titre 2 Chapitre 2-1 du Règlement départemental d'Aide Sociale PA PH de l'Eure et Loir
                   L’aide sociale à l’hébergement en établissement s’adresse aux personnes résidant en EHPAD, en résidence autonomie ou en USLD et dont les ressources ne permettent pas de faire face aux frais d’hébergement. 
                   Les ressources de la personne (hors prestations familiales) sont récupérées dans la limite de 90% (AL et APL récupérées à 100%).
                   Cette aide fait l’objet d’une récupération sur succession.
                """

    def formula_2020_01(individu,period,parameters):
        age = individu('age', period)
        inapte_travail = individu('inapte_travail', period)
        ressortissant_eee = individu('ressortissant_eee', period)
        duree_possession_titre_sejour = individu('duree_possession_titre_sejour', period)
        individual_resource_names = {
            'ass',
            'chomage_net',
            'retraite_nette',
            'salaire_net',
            'allocation_securisation_professionnelle',
            'dedommagement_victime_amiante',
            'gains_exceptionnels',
            'indemnites_chomage_partiel',
            'indemnites_journalieres',
            'indemnites_volontariat',
            'pensions_invalidite',
            'prestation_compensatoire',
            'prime_forfaitaire_mensuelle_reprise_activite',
            'retraite_brute',
            'revenus_stage_formation_pro',
            'rsa_base_ressources_patrimoine_individu'
        }

        individu_resources = sum([individu(resource, period.last_month) for resource in individual_resource_names])

        condition_age = ((age >= parameters(
            period).departements.eure_et_loir.ASH.age_minimal_personne_agee_apte_travail) or (
                                     age >= parameters(
                                 period).departements.eure_et_loir.ASH.age_minimal_personne_agee_inapte_travail and inapte_travail))
        condition_nationalite = ressortissant_eee if ressortissant_eee else duree_possession_titre_sejour >0
        condition_ressources = individu_resources <= individu.menage('loyer',period)

        # Attention le loyer ici est défini sur un mois alors que les tarifs des établissements sont journaliers
        # Auquel sera ajouté individu('dependance_tarif_etablissement_gir_5_6',period) * nb de jours * tarif_journalier

        return condition_age * condition_nationalite * condition_ressources

class eure_et_loir_ASH_personne_handicap(Variable):
    value_type = bool
    entity = Individu
    definition_period = MONTH
    label = "Éligibilité d'une personne en sitaution de handicap à l'aide sociale à l'hébergement en établisement"
    reference = """Titre 2 Chapitre 3-1 du Règlement départemental d'Aide Sociale PA PH de l'Eure et Loir
                   Toute personne âgée de 18 ans et plus, dont l’état de santé ou le handicap nécessite l’entrée en établissement social ou médico-social (hébergement permanent, hébergement temporaire, accueil de jour), peut bénéficier d’une prise en charge des frais de séjour en foyer d’hébergement, en foyer occupationnel, en foyer de vie, en foyer d’accueil médicalisé. Le bénéficiaire contribue aux frais de séjour dans des conditions définies dans le cadre du règlement départemental d’aide sociale. 
                    Cette aide doit faire l’objet d’une décision d’orientation de la Maison départementale de l’autonomie (MDA).
                """

    def formula_2020_01(individu,period,parameters):
        age = individu('age', period)
        ressortissant_eee = individu('ressortissant_eee', period)
        duree_possession_titre_sejour = individu('duree_possession_titre_sejour', period)
        situation_handicap = individu('handicap',period)

        condition_age = (age >= parameters(period).departements.eure_et_loir.ASH.age_minimal_personne_handicap)
        condition_nationalite = ressortissant_eee if ressortissant_eee else duree_possession_titre_sejour >0
        condition_handicap = situation_handicap

        return condition_age * condition_nationalite * condition_handicap
