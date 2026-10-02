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
Le principe est maintenant : ces règles permanentes vont dans AGENTS.md et je ne les recopierai plus dans chaque prompt Codex. Les futurs prompts pourront essentiellement contenir l’objectif + le comportement attendu + les particularités de l’étape.
