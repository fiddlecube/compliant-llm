# flake8: noqa: E501
import tqdm
from pydantic import BaseModel
from tqdm.asyncio import tqdm as async_tqdm_bar

from core.strategies._attack_enhancers.base import AttackEnhancementResult
from core.strategies._attack_enhancers.basic_attacks.base import AttackEnhancement
from core.providers.litellm_provider import LiteLLMProvider

from .schema import ComplianceData, EnhancedAttack, IsGrayBox
from .template import GrayBoxTemplate


class GrayBox(AttackEnhancement):
    def __init__(self, synthesizer_model: LiteLLMProvider):
        self.synthesizer_model = synthesizer_model

    ##################################################
    ### Sync GrayBox Attack - enhance ################
    ##################################################

    def enhance(
        self, attack: str, max_retries: int = 5
    ) -> AttackEnhancementResult:
        """Enhance the attack synchronously with compliance checking and a single progress bar."""
        prompt = GrayBoxTemplate.enhance(attack)

        # Progress bar for retries (total count is double the retries: 1 for generation, 1 for compliance check)
        with tqdm(
            total=max_retries * 3,
            desc="...... 🔓 Gray Box",
            unit="step",
            leave=False,
        ) as pbar:
            for _ in range(max_retries):
                # Generate the enhanced attack
                res: EnhancedAttack = self._generate_schema(
                    prompt, EnhancedAttack
                )
                enhanced_attack = res.input
                pbar.update(1)  # Update the progress bar for generation

                # Check for compliance using a compliance template
                compliance_prompt = GrayBoxTemplate.non_compliant(
                    res.model_dump()
                )
                compliance_res: ComplianceData = self._generate_schema(
                    compliance_prompt, ComplianceData
                )
                pbar.update(1)  # Update the progress bar for compliance

                # Check if rewritten prompt is a gray box attack
                is_gray_box_prompt = GrayBoxTemplate.is_gray_box(
                    res.model_dump()
                )
                is_gray_box_res: IsGrayBox = self._generate_schema(
                    is_gray_box_prompt, IsGrayBox
                )
                pbar.update(
                    1
                )  # Update the progress bar for is gray box attack

                if (
                    not compliance_res.non_compliant
                    and is_gray_box_res.is_gray_box
                ):
                    # If it's compliant and is a gray box attack, return the enhanced prompt
                    return AttackEnhancementResult(
                        output_text=enhanced_attack,
                        output_type="text",
                        metadata={"attack_enhancement": "gray_box"},
                    )

        # If all retries fail, return the original attack
        return AttackEnhancementResult(
            output_text=attack,
            output_type="text",
            metadata={"attack_enhancement": "gray_box"},
        )

    ##################################################
    ### Async GrayBox Attack - a_enhance #############
    ##################################################

    async def a_enhance(
        self, attack: str, max_retries: int = 5
    ) -> AttackEnhancementResult:
        """Enhance the attack asynchronously with compliance checking and a single progress bar."""
        prompt = GrayBoxTemplate.enhance(attack)

        # Async progress bar for retries (double the count to cover both generation and compliance check)
        pbar = async_tqdm_bar(
            total=max_retries * 3,
            desc="...... 🔓 Gray Box",
            unit="step",
            leave=False,
        )

        try:
            for _ in range(max_retries):
                # Generate the enhanced attack asynchronously
                res: EnhancedAttack = await self._a_generate_schema(
                    prompt, EnhancedAttack
                )
                enhanced_attack = res.input
                pbar.update(1)  # Update the progress bar for generation

                # Check for compliance using a compliance template
                compliance_prompt = GrayBoxTemplate.non_compliant(
                    res.model_dump()
                )
                compliance_res: ComplianceData = await self._a_generate_schema(
                    compliance_prompt, ComplianceData
                )
                pbar.update(1)  # Update the progress bar for compliance

                # Check if rewritten prompt is a gray box attack
                is_gray_box_prompt = GrayBoxTemplate.is_gray_box(
                    res.model_dump()
                )
                is_gray_box_res: IsGrayBox = await self._a_generate_schema(
                    is_gray_box_prompt, IsGrayBox
                )
                pbar.update(
                    1
                )  # Update the progress bar for is gray box attack

                if (
                    not compliance_res.non_compliant
                    and is_gray_box_res.is_gray_box
                ):
                    # If it's compliant and is a gray box attack, return the enhanced prompt
                    return AttackEnhancementResult(
                        output_text=enhanced_attack,
                        output_type="text",
                        metadata={"attack_enhancement": "gray_box"},
                    )

        finally:
            # Close the progress bar after the loop
            pbar.close()

        # If all retries fail, return the original attack
        return AttackEnhancementResult(attack, "text")

    ##################################################
    ### Helper Methods ###############################
    ##################################################

    def _generate_schema(self, prompt: str, schema: BaseModel):
        """Helper method to generate the schema synchronously."""
        return self.synthesizer_model.generate_schema(prompt, schema)

    async def _a_generate_schema(self, prompt: str, schema: BaseModel):
        """Helper method to generate the schema asynchronously."""
        return await self.synthesizer_model.agenerate_schema(prompt, schema)
