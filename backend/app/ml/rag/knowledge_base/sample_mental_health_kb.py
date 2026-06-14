"""
Sample Mental Health Knowledge Base
Diverse, culturally-sensitive mental health content
"""

# CBT (Cognitive Behavioral Therapy) Techniques
CBT_DOCUMENTS = [
    {
        "text": """
        Cognitive Behavioral Therapy (CBT) - Thought Record Technique

        The thought record is a core CBT technique for identifying and challenging negative thoughts.

        Steps:
        1. Situation: Describe what happened that triggered the negative emotion
        2. Emotions: Identify the emotions you felt (e.g., anxious, sad, angry)
        3. Automatic Thoughts: Write down the thoughts that went through your mind
        4. Evidence For: List evidence supporting the thought
        5. Evidence Against: List evidence that contradicts the thought
        6. Alternative Thought: Create a more balanced, realistic thought
        7. Re-rate Emotions: Notice how your emotions change

        This technique helps you recognize cognitive distortions like catastrophizing,
        black-and-white thinking, and overgeneralization.
        """,
        "category": "cbt",
        "source": "CBT Fundamentals",
        "culture": "universal",
        "topic": "anxiety_depression"
    },
    {
        "text": """
        Behavioral Activation for Depression

        Behavioral activation is an evidence-based CBT technique for treating depression.
        It focuses on scheduling and engaging in activities that bring pleasure or accomplishment.

        Key principles:
        - Depression often leads to withdrawal and avoidance
        - Inactivity maintains depression
        - Engaging in valued activities improves mood

        Steps:
        1. Monitor current activities and mood
        2. Identify values-based activities
        3. Schedule activities in advance
        4. Start small and build gradually
        5. Track completion and mood changes

        Activities can include: social connection, exercise, hobbies, self-care,
        helping others, or learning something new.
        """,
        "category": "cbt",
        "source": "Behavioral Activation Protocol",
        "culture": "universal",
        "topic": "depression"
    }
]

# Mindfulness and Meditation
MINDFULNESS_DOCUMENTS = [
    {
        "text": """
        Mindfulness-Based Stress Reduction (MBSR)

        MBSR is an evidence-based program combining mindfulness meditation and yoga
        to help manage stress, anxiety, and pain.

        Core practices:
        1. Body Scan: Systematically focus attention on different body parts
        2. Sitting Meditation: Focus on breath, body sensations, or sounds
        3. Mindful Movement: Gentle yoga with attention to bodily sensations
        4. Loving-Kindness Meditation: Cultivate compassion for self and others

        Benefits:
        - Reduced stress and anxiety
        - Improved emotional regulation
        - Better pain management
        - Enhanced self-awareness
        - Improved sleep quality

        Practice recommendation: Start with 5-10 minutes daily,
        gradually increasing to 20-30 minutes.
        """,
        "category": "mindfulness",
        "source": "MBSR Guidelines",
        "culture": "universal",
        "topic": "stress_anxiety"
    },
    {
        "text": """
        5-4-3-2-1 Grounding Technique

        This mindfulness technique helps manage anxiety, panic attacks, and dissociation
        by grounding you in the present moment using your five senses.

        Steps:
        1. Five: Acknowledge 5 things you can see around you
        2. Four: Acknowledge 4 things you can touch/feel
        3. Three: Acknowledge 3 things you can hear
        4. Two: Acknowledge 2 things you can smell
        5. One: Acknowledge 1 thing you can taste

        This technique is particularly helpful during:
        - Panic attacks
        - Flashbacks or dissociation
        - Overwhelming anxiety
        - Intrusive thoughts

        Practice regularly to make it more effective during crisis moments.
        """,
        "category": "mindfulness",
        "source": "Grounding Techniques",
        "culture": "universal",
        "topic": "anxiety_panic_ptsd"
    }
]

# Culturally-Adapted Interventions
CULTURAL_DOCUMENTS = [
    {
        "text": """
        Collectivist Approaches to Mental Health (Asian Cultural Context)

        In many Asian cultures, mental health is viewed through a collectivist lens
        where family harmony and social relationships are central.

        Key considerations:
        - Family involvement: Include family in treatment when appropriate
        - Indirect communication: Respect for hierarchy may affect disclosure
        - Somatic expressions: Distress may manifest as physical symptoms
        - Face-saving: Avoid direct confrontation or blame
        - Filial piety: Respect for elders impacts decision-making

        Culturally-adapted strategies:
        - Frame therapy as skill-building rather than "fixing problems"
        - Acknowledge family obligations and roles
        - Use metaphors and stories
        - Integrate mindfulness practices (e.g., Buddhist meditation)
        - Address stigma sensitively

        Avoid: Overemphasis on individual autonomy, direct confrontation with family members
        """,
        "category": "cultural",
        "source": "Culturally-Adapted CBT for Asian Populations",
        "culture": "asian_collectivist",
        "topic": "cultural_adaptation"
    },
    {
        "text": """
        Ubuntu Philosophy in African Mental Health

        Ubuntu ("I am because we are") is a Southern African philosophy emphasizing
        interconnectedness, community, and shared humanity.

        Mental health through Ubuntu lens:
        - Healing occurs in community, not isolation
        - Distress affects the whole community
        - Storytelling and oral traditions as healing
        - Connection to ancestors and spirituality
        - Collective problem-solving

        Therapeutic approaches:
        - Group-based interventions
        - Community healing circles
        - Integration of spiritual practices
        - Narrative therapy using cultural stories
        - Family and community involvement

        Coping strategies rooted in Ubuntu:
        - Seek support from elders and community
        - Participate in cultural rituals
        - Contribute to community well-being
        - Draw strength from shared experiences
        """,
        "category": "cultural",
        "source": "Ubuntu-Based Mental Health Interventions",
        "culture": "african",
        "topic": "cultural_adaptation_community"
    },
    {
        "text": """
        Latinx Mental Health: Familismo and Personalismo

        Latinx cultures often emphasize familismo (family unity) and personalismo
        (warm personal relationships).

        Cultural values:
        - Familismo: Strong family bonds and loyalty
        - Personalismo: Preference for warm, personal interactions
        - Respeto: Respect for authority and elders
        - Simpatía: Maintaining harmony in relationships

        Mental health implications:
        - Family support is crucial protective factor
        - May delay seeking help due to stigma (vergüenza)
        - Trust-building is essential
        - Faith and spirituality play important role

        Culturally-responsive approaches:
        - Build warm, personal therapeutic relationship
        - Involve family when appropriate
        - Respect spiritual/religious beliefs
        - Address acculturation stress
        - Use dichos (proverbs) and cultural metaphors
        - Provide services in Spanish when needed
        """,
        "category": "cultural",
        "source": "Latinx Mental Health Guidelines",
        "culture": "latinx",
        "topic": "cultural_adaptation_family"
    }
]

# Crisis Intervention
CRISIS_DOCUMENTS = [
    {
        "text": """
        Suicide Risk Assessment and Safety Planning

        Warning signs of suicide risk:
        - Talking about wanting to die or kill oneself
        - Looking for ways to kill oneself (researching methods)
        - Talking about feeling hopeless or having no purpose
        - Feeling trapped or in unbearable pain
        - Talking about being a burden to others
        - Increasing use of alcohol or drugs
        - Withdrawing from activities and people
        - Giving away possessions
        - Saying goodbye to people

        Immediate actions:
        1. Ask directly about suicidal thoughts
        2. Listen without judgment
        3. Do not leave person alone if at imminent risk
        4. Remove access to lethal means
        5. Call crisis hotline or emergency services

        Crisis resources:
        - National Suicide Prevention Lifeline: 988 (US)
        - Crisis Text Line: Text HOME to 741741
        - International Association for Suicide Prevention: www.iasp.info

        Safety planning includes:
        - Identifying warning signs
        - Internal coping strategies
        - Social contacts for distraction
        - Family/friends who can help
        - Professional contacts
        - Making environment safe
        """,
        "category": "crisis",
        "source": "Suicide Prevention Protocol",
        "culture": "universal",
        "topic": "suicide_crisis"
    },
    {
        "text": """
        De-escalation Techniques for Acute Distress

        When someone is in acute emotional distress or crisis:

        Do:
        - Stay calm and speak in a gentle, reassuring tone
        - Use active listening and validation
        - Give the person space and time
        - Acknowledge their feelings without judgment
        - Use simple, clear language
        - Offer choices to restore sense of control
        - Focus on the present moment

        Don't:
        - Argue or challenge their perceptions
        - Use threatening language or gestures
        - Make false promises
        - Dismiss or minimize their feelings
        - Crowd their personal space
        - Rush the conversation

        Grounding techniques for acute anxiety:
        - Deep breathing (4-7-8 technique)
        - 5-4-3-2-1 sensory grounding
        - Progressive muscle relaxation
        - Cold water on face (dive reflex)
        - Holding ice cubes

        If situation escalates, seek immediate professional help.
        """,
        "category": "crisis",
        "source": "Crisis De-escalation Guidelines",
        "culture": "universal",
        "topic": "crisis_deescalation"
    }
]

# Trauma-Informed Care
TRAUMA_DOCUMENTS = [
    {
        "text": """
        Trauma-Informed Principles

        Trauma-informed care recognizes the widespread impact of trauma and
        understands paths to recovery.

        Core principles (6 R's):
        1. Realize: Understand trauma's widespread impact
        2. Recognize: Identify signs of trauma in individuals
        3. Respond: Apply trauma knowledge to practice
        4. Resist Re-traumatization: Avoid triggering trauma responses
        5. Resilience: Focus on strengths and recovery
        6. Respect: Honor cultural and individual differences

        Trauma responses:
        - Fight: Anger, aggression, control
        - Flight: Avoidance, withdrawal, panic
        - Freeze: Shutdown, dissociation, numbness
        - Fawn: People-pleasing, over-compliance

        Supporting trauma survivors:
        - Create physical and emotional safety
        - Build trust through consistency
        - Offer choice and control
        - Validate experiences
        - Emphasize strengths and resilience
        - Proceed at survivor's pace
        - Address cultural and identity factors
        """,
        "category": "trauma",
        "source": "Trauma-Informed Care Framework",
        "culture": "universal",
        "topic": "trauma_ptsd"
    }
]

# Self-Care and Wellness
SELFCARE_DOCUMENTS = [
    {
        "text": """
        Holistic Self-Care Strategies

        Self-care encompasses multiple dimensions of wellness:

        Physical Self-Care:
        - Regular sleep schedule (7-9 hours)
        - Nutritious meals
        - Regular exercise (even 10-minute walks)
        - Limit alcohol and caffeine
        - Medical check-ups

        Emotional Self-Care:
        - Journaling
        - Therapy or counseling
        - Expressing emotions healthily
        - Setting boundaries
        - Practicing self-compassion

        Social Self-Care:
        - Quality time with loved ones
        - Join support groups
        - Maintain friendships
        - Ask for help when needed

        Spiritual Self-Care:
        - Meditation or prayer
        - Time in nature
        - Engaging with values
        - Creative expression

        Mental Self-Care:
        - Learning new skills
        - Reading
        - Limiting news/social media
        - Puzzles or games

        Self-care is not selfish—it's essential for well-being.
        """,
        "category": "selfcare",
        "source": "Wellness Guidelines",
        "culture": "universal",
        "topic": "wellness_prevention"
    }
]

# Anxiety Management
ANXIETY_DOCUMENTS = [
    {
        "text": """
        Evidence-Based Anxiety Management Techniques

        Breathing Exercises:
        1. Diaphragmatic Breathing: Breathe deeply from belly, not chest
        2. 4-7-8 Breathing: Inhale 4 counts, hold 7, exhale 8
        3. Box Breathing: Inhale 4, hold 4, exhale 4, hold 4

        Cognitive Techniques:
        - Challenge anxious thoughts (Is this thought realistic?)
        - Decatastrophize (What's the worst/best/most likely outcome?)
        - Postpone worry (Schedule "worry time" for later)
        - Accept uncertainty (Practice tolerating "not knowing")

        Behavioral Techniques:
        - Gradual exposure to feared situations
        - Problem-solving for controllable concerns
        - Progressive muscle relaxation
        - Regular exercise

        Lifestyle Factors:
        - Limit caffeine and alcohol
        - Maintain sleep hygiene
        - Regular meals
        - Social connection

        When to seek professional help:
        - Anxiety interferes with daily life
        - Panic attacks
        - Avoidance of important activities
        - Physical symptoms (chest pain, dizziness)
        """,
        "category": "anxiety",
        "source": "Anxiety Management Protocols",
        "culture": "universal",
        "topic": "anxiety_management"
    }
]

# Depression Support
DEPRESSION_DOCUMENTS = [
    {
        "text": """
        Understanding and Managing Depression

        Common symptoms:
        - Persistent sad or empty mood
        - Loss of interest in activities
        - Changes in appetite or weight
        - Sleep disturbances
        - Fatigue or low energy
        - Difficulty concentrating
        - Feelings of worthlessness or guilt
        - Thoughts of death or suicide

        Evidence-based treatments:
        - Psychotherapy (CBT, IPT, behavioral activation)
        - Medication (antidepressants) when appropriate
        - Exercise (as effective as medication for mild-moderate depression)
        - Light therapy (for seasonal depression)
        - Social support

        Self-help strategies:
        - Maintain routine and structure
        - Set small, achievable goals
        - Exercise regularly (even 10-minute walks)
        - Practice self-compassion
        - Stay connected to others
        - Avoid alcohol and drugs
        - Challenge negative thoughts
        - Engage in pleasant activities

        When to seek immediate help:
        - Suicidal thoughts or plans
        - Self-harm urges
        - Inability to function in daily life
        - Psychotic symptoms
        """,
        "category": "depression",
        "source": "Depression Treatment Guidelines",
        "culture": "universal",
        "topic": "depression_treatment"
    }
]

# Compile all documents
ALL_DOCUMENTS = (
    CBT_DOCUMENTS +
    MINDFULNESS_DOCUMENTS +
    CULTURAL_DOCUMENTS +
    CRISIS_DOCUMENTS +
    TRAUMA_DOCUMENTS +
    SELFCARE_DOCUMENTS +
    ANXIETY_DOCUMENTS +
    DEPRESSION_DOCUMENTS
)


def get_sample_knowledge_base():
    """Get all sample documents"""
    return ALL_DOCUMENTS


def get_documents_by_category(category: str):
    """Get documents by category"""
    return [doc for doc in ALL_DOCUMENTS if doc.get("category") == category]


def get_documents_by_culture(culture: str):
    """Get documents by culture"""
    return [doc for doc in ALL_DOCUMENTS if doc.get("culture") == culture]


def get_categories():
    """Get all available categories"""
    return list(set(doc.get("category") for doc in ALL_DOCUMENTS))


def get_cultures():
    """Get all available cultures"""
    return list(set(doc.get("culture") for doc in ALL_DOCUMENTS))
