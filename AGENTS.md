1. Lire avant de modifier
   - Lire le code existant et les fichiers concernés.
   - Comprendre le flux actuel avant tout changement.
   - Respecter les décisions d’architecture existantes.
   - Ne pas inventer une décision d’architecture en cas d’ambiguïté importante.
2. Respecter strictement le scope
   - Modifier uniquement ce qui est demandé.
   - Ne pas anticiper les prochaines étapes.
   - Aucun refactoring hors scope.
   - Ne pas renommer/déplacer/supprimer des éléments sans nécessité.
   - Ne pas modifier une API ou structure de données sans demande explicite.
3. Respecter l’architecture
   - Conserver les responsabilités des classes.
   - Réutiliser l’existant avant de créer de nouvelles méthodes.
   - Ne pas dupliquer de logique.
   - Ne pas créer de nouvelles couches ou abstractions inutilement.
   - Ne pas contourner les interfaces publiques pour manipuler directement l’état interne.
4. Règles spécifiques au Viewer
   - Conserver la séparation ST_Command / ST_Job.
   - ST_Command représente une commande reçue.
   - ST_Job représente le travail nécessaire au flux d’ouverture.
   - OPEN peut créer un ST_Job.
   - SHOW, HIDE, CLOSE ne créent pas de ST_Job, sauf nouvelle décision architecturale.
   - ViewerController.process_command() assure le routage.
   - SectionManager reste responsable de la gestion des sections.
   - Réutiliser show_section(), hide_section() et close_section().
   - Conserver actuellement file_name + file_path pour identifier les fichiers.
   - CommandManager est responsable de construire file_name et file_path en amont lors de la création de ST_Command.
   - ST_Command transporte explicitement file_name et file_path ; les couches suivantes les consomment tels quels.
   - Ne pas reconstruire file_name à partir de file_path dans ViewerController, SectionManager ou une autre couche en aval.
5. Tests
   - Ne jamais supprimer ou affaiblir un test simplement pour faire passer le code.
   - Modifier un test uniquement si le comportement attendu a réellement changé.
   - Ajouter les tests nécessaires pour les nouveaux comportements.
   - Exécuter les tests pertinents.
   - Vérifier syntaxe et imports.
   - Chercher la vraie cause d’un test en échec avant de modifier quoi que ce soit.
6. Qualité du code
   - Changements simples et cohérents avec le style existant.
   - Pas de commentaires ligne par ligne.
   - Commentaires uniquement lorsqu’ils apportent une information utile.
   - Supprimer/corriger les commentaires devenus faux.
   - Pas de code mort, placeholder ou TODO inutile.
7. Git
   - Aucun commit sans demande explicite.
   - Aucun push sans demande explicite.
   - Ne pas réécrire l’historique Git.
   - Ne pas toucher aux modifications utilisateur sans rapport avec la tâche.
8. Compte rendu obligatoire
   - Fichiers modifiés.
   - Changements effectués.
   - Tests/vérifications exécutés.
   - Résultats.
   - Points restant éventuellement à décider.
9. Commentaires dans le code
- Ajouter uniquement des commentaires courts et utiles.
- Ne pas commenter une ligne lorsque son fonctionnement est évident.
- Ne pas répéter en commentaire ce que le code exprime déjà clairement.
- Lorsqu'un comportement change, modifier ou supprimer les commentaires devenus obsolètes.
10. Organisation des déclarations
- Regrouper les déclarations et instanciations de classes entre elles afin de garder le code ordonné et lisible.
- Éviter de disperser les créations d'instances au milieu d'autres traitements lorsqu'elles peuvent être regroupées.
- Conserver un ordre cohérent et facilement identifiable pour les différents composants.
11. Nomenclature des classes et de leurs instances
   - Toute classe métier ou composant utilise le préfixe `CLS_` suivi du nom en PascalCase.
   - Exemple : `CLS_CommandManager`, `CLS_SectionManager`, `CLS_LayoutManager`.
   - Toute instance d'une classe `CLS_*` utilise le préfixe `cls` suivi du nom de la classe en PascalCase, sans le préfixe `CLS_`.
   - Exemple : `CLS_CommandManager` → `clsCommandManager`.
   - Exemple : `CLS_SectionManager` → `clsSectionManager`.
   - Exemple : `CLS_LayoutManager` → `clsLayoutManager`.
   - Exemple : `CLS_PlatformAdapter` → `clsPlatformAdapter`.
   - Exemple : `CLS_TimerLifecycleManager` → `clsTimerLifecycleManager`.
   - Exemple : `CLS_ViewerController` → `clsViewerController`.

12. Nomenclature des attributs et paramètres contenant des classes
   - Un attribut privé contenant une instance d'une classe `CLS_*` utilise `_clsNomDeClasse`.
   - Exemple : `_clsSectionManager`, `_clsLayoutManager`, `_clsTimerLifecycleManager`.
   - Un paramètre représentant une instance d'une classe `CLS_*` utilise également `clsNomDeClasse`.
   - Ne pas utiliser `snake_case` pour nommer une instance d'une classe `CLS_*`.
   - Exemple incorrect : `section_manager`.
   - Exemple correct : `clsSectionManager`.
13. Nomenclature des structures et de leurs instances
   - Toute structure utilise le préfixe `ST_` suivi du nom de la structure en PascalCase.
   - Exemple : `ST_Command`, `ST_Job`, `ST_JobSection`, `ST_JobLayout`, `ST_JobLifecycle`.
   - Toute instance d'une structure `ST_*` utilise le préfixe `st` suivi du nom de la structure en PascalCase, sans le préfixe `ST_`.
   - Exemple : `ST_Command` → `stCommand`.
   - Exemple : `ST_Job` → `stJob`.
   - Exemple : `ST_JobSection` → `stJobSection`.
   - Exemple : `ST_JobLayout` → `stJobLayout`.
   - Exemple : `ST_JobLifecycle` → `stJobLifecycle`.
   - Un attribut privé contenant une structure utilise `_stNomDeStructure`.
   - Exemple : `_stJob`, `_stJobLayout`.
   - Un paramètre représentant une structure utilise également `stNomDeStructure`.
   - Ne pas utiliser `snake_case` pour nommer une instance d'une structure `ST_*`.
   - Exemple incorrect : `st_job`, `job_layout`.
   - Exemple correct : `stJob`, `stJobLayout`.
