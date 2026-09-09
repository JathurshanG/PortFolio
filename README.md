# Jathurshan G — Portfolio Data

Portfolio statique en français consacré au Data Engineering, à la recommandation IA et à l’analytics.

[Accueil](https://jathurshang.github.io/PortFolio/) · [Projets](https://jathurshang.github.io/PortFolio/projects.html)

## Fichiers

| Fichier | Rôle |
| --- | --- |
| `index.html` | Accueil, expertises, projets et contact |
| `projects.html` | Présentation détaillée des trois projets, avec ancres sémantiques |
| `assets/css/style.css` | Styles communs, responsive, focus clavier, réduction des animations et impression |
| `robots.txt` | Directives prêtes à publier à la racine de l’hôte |
| `sitemap.xml` | Les deux URL canoniques du portfolio |
| `google2152c437bb871421.html` | Fichier de validation Google conservé à l’identique |
| `scripts/check_site.py` | Vérification locale des liens, métadonnées, ancres et fichiers SEO |
| `.github/workflows/sitemap.yml` | Validation sur les push et pull requests vers master |

Aucune compilation, installation npm ou dépendance JavaScript n’est nécessaire. Les polices système évitent les requêtes à Google Fonts. Un seul fichier CSS est partagé par les deux pages.

## Intégration

Remplacer les deux fichiers HTML et le fichier CSS ensemble, ainsi que le sitemap. Supprimer l’ancien `robot.txt` et ajouter `robots.txt`. Conserver le fichier Google exactement à son emplacement actuel.

Le workflow valide les fichiers sur `master`, la branche par défaut du dépôt. Il remplace l’ancien générateur ciblant `main` et ne crée plus de commits automatiques. Le sitemap est explicite : pour deux pages, cela évite d’indexer les fichiers de validation ou des URL inexistantes. Lors de l’ajout d’une page, ajouter son URL canonique au sitemap.

La mise en ligne continue de dépendre de la configuration GitHub Pages existante. Aucun hébergement supplémentaire n’est créé.

## Attention à la portée de robots.txt

La racine du dépôt et la racine de l’hôte sont différentes pour un site de projet GitHub Pages :

| URL | Traitement |
| --- | --- |
| `https://jathurshang.github.io/robots.txt` | Emplacement consulté par les robots pour cet hôte |
| `https://jathurshang.github.io/PortFolio/robots.txt` | Sous-répertoire ; non consulté comme fichier de règles |

Le renommage corrige le dépôt, mais il faut aussi publier ces directives à la racine de l’hôte pour qu’elles soient découvertes. Cela passe habituellement par la source du site utilisateur `JathurshanG.github.io`, si celui-ci existe et sert cette racine. Si un fichier robots existe déjà à cet emplacement, conserver ses règles et ajouter la ligne Sitemap appropriée. Ce changement ne fait pas partie de ce dépôt.

L’absence de robots.txt n’interdit pas l’exploration. Google traite notamment une réponse 404 comme l’absence de restrictions. Une réponse serveur 5xx ou une règle Disallow peut avoir un effet différent. L’état HTTP du fichier à la racine de l’hôte n’a pas été établi lors de cette refonte.

[Documentation Google sur robots.txt](https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec)

## Sitemap et Search Console

Le sitemap utilise l’espace de noms standard `http://www.sitemaps.org/schemas/sitemap/0.9` ; les URL du site restent en HTTPS. Il contient uniquement :

- `https://jathurshang.github.io/PortFolio/`
- `https://jathurshang.github.io/PortFolio/projects.html`

Les fragments ne sont pas des pages indépendantes. Les champs facultatifs priority et changefreq ont été retirés ; aucun lastmod artificiel n’est ajouté.

Après publication, soumettre `https://jathurshang.github.io/PortFolio/sitemap.xml` dans la propriété Search Console correspondante. Le fichier de validation est conservé à l’URL suivante, sans ajout de lien dans la navigation :

`https://jathurshang.github.io/PortFolio/google2152c437bb871421.html`

Cette présence conserve le mécanisme existant ; elle ne permet pas de confirmer l’état de validation dans le compte Search Console.

[Protocole Sitemaps](https://www.sitemaps.org/protocol.html)

## Contenu et liens

Les descriptions reprennent les trois projets déjà présents dans le dépôt. Aucun chiffre de performance, volume de données, client, dépôt de code ou lien de démonstration n’a été inventé. La préparation d’une API REST est décrite comme une intégration envisagée ; SQL apparaît comme un usage analytique en aval, pas comme une brique de stockage attestée.

| Projet | Fragment courant | Ancien fragment encore reconnu |
| --- | --- | --- |
| Pipeline ETL skincare | `#skincare-etl-pipeline` | `#project-1` |
| Recommandation IA | `#skincare-ai-recommender` | `#project-2` |
| Tableau de bord analytics | `#portfolio-analytics-dashboard` | `#project-3` |

Les anciens fragments sont des alias d’ancrage pour préserver les liens déjà partagés ; les nouveaux liens et articles utilisent les noms sémantiques.

L’adresse de contact `hello@jathurshan.com` est reprise des pages existantes. Sa réception n’a pas été vérifiée ; confirmer cette adresse avant publication.

## Métadonnées et partage

Chaque page possède un titre et une description distincts, une URL canonique, les métadonnées Open Graph et Twitter Card. Aucun visuel de partage n’existait dans le dépôt : aucune URL d’image fictive n’a été ajoutée. Le rendu final des aperçus dépend de chaque plateforme.

Le JSON-LD décrit la personne et les projets visibles, avec Person, CollectionPage, ItemList et CreativeWork. Ce balisage aide à décrire le contenu ; il ne garantit ni résultat enrichi ni classement Google. Le bloc `application/ld+json` est une donnée, pas un script exécutable : defer/async ne lui est pas applicable.

[CreativeWork sur Schema.org](https://schema.org/CreativeWork)

## Vérification

Depuis la racine du dépôt, avec Python 3.10 ou plus récent :

```bash
python3 scripts/check_site.py
```

Le contrôle vérifie les références locales et leurs fragments, la hiérarchie des titres, les noms des liens et des navigations, les références ARIA, la cohérence des métadonnées et du JSON-LD, le sitemap, les directives robots et l’intégrité du fichier Google.

Les styles prévoient le repli des colonnes, le retour à la ligne des libellés, un focus visible, un lien d’évitement et la préférence reduced-motion. La navigation reste visible sans JavaScript. Aucun score Lighthouse, Core Web Vitals ni audit WCAG complet n’est revendiqué : le contrôle automatique ne remplace pas un essai réel au clavier, sur mobile, avec zoom et lecteur d’écran.

