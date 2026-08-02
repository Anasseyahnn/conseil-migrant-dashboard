# Product

## Register

product

## Users

L'équipe opérationnelle de Conseil Migrant : personnes qui suivent au
quotidien les besoins exprimés par des bénéficiaires (population migrante
vulnérable) — volume, taux de prise en charge, répartition par profil,
géographie, évolution temporelle. Contexte d'usage : poste de travail,
consultation régulière pendant l'activité de terrain/suivi de dossiers, pas
un usage grand public.

## Product Purpose

Tableau de bord opérationnel (Streamlit) donnant une vue synthétique et
fiable de l'activité de Conseil Migrant, pour appuyer des décisions réelles
sur des bénéficiaires — pas un outil de démonstration. L'app est publique et
indexable sur Streamlit Cloud (contrainte de plan), donc une page de
connexion applicative (`src/auth.py`) est la seule protection avant
d'afficher des données réelles (PII d'une population vulnérable).

## Brand Personality

Chaleureux, humain, rassurant — sans jamais sacrifier la clarté ni la
crédibilité institutionnelle du sujet traité. La chaleur passe par la
typographie (Fraunces en titrage) et une palette douce déjà validée
(`src/palette.py`), pas par des effets décoratifs.

## Anti-references

Pas d'esthétique "SaaS générique" : pas de dégradés décoratifs sur le texte,
pas de cartes empilées sans raison, pas de glassmorphism, pas de gros chiffre
hero avec halo. L'app sert un usage social/institutionnel réel, pas un
produit commercial à vendre.

## Design Principles

- La confiance avant l'effet : chaque choix visuel doit renforcer la
  crédibilité d'un outil qui traite des données réelles sur une population
  vulnérable.
- Cohérence avec le système existant : réutiliser la palette et les polices
  déjà validées (`src/palette.py`, `src/ui.py`) plutôt qu'en introduire de
  nouvelles.
- Clarté opérationnelle d'abord : la page de connexion doit rassurer
  immédiatement sur la nature sérieuse de l'outil (pas de doute sur sa
  légitimité au premier coup d'œil).
- Sobriété assumée : la chaleur vient du détail (typographie, micro-motion,
  teintes douces), jamais de la décoration gratuite.

## Accessibility & Inclusion

Contraste texte ≥ 4.5:1 sur tous les champs, y compris les placeholders.
Formulaire de connexion utilisable au clavier seul. Respect de
`prefers-reduced-motion` pour toute animation ajoutée.
