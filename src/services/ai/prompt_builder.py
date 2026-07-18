from src.services.ai.prompts import (
    SYSTEM_PROMPT,
    SUMMARY_PROMPT,
)



class PromptBuilder:
    """
    Builds AI prompts.
    """


    def system_prompt(self):

        return SYSTEM_PROMPT



    def summary_prompt(
        self,
        transcript: str,
        language: str,
        summary_type: str,
    ):
        """
        Build summary prompt based on user preference.
        """


        if summary_type == "fast":

            style_instruction = """
Create a short summary.

Focus only on:
- Main idea
- Important points
- Final conclusion

Avoid unnecessary details.
"""


        elif summary_type == "learning":

            style_instruction = """
Create an educational explanation.

Explain:
- Concepts step by step
- Important definitions
- Examples
- Practical usage

Write like a teacher explaining to a student.
"""


        else:

            style_instruction = """
Create a detailed professional summary.

Include:
- Full explanation
- Main ideas
- Important concepts
- Examples
- Tools and resources
- Practical actions
"""



        return SUMMARY_PROMPT.format(
            language=language,
            style_instruction=style_instruction,
            transcript=transcript,
        )