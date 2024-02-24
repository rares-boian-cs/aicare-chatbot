import datetime

from common.constant import EIT, MFST, MIT


class MatterService:
    def __init__(self):
        self.flow = {
            EIT.CHOICE: {
                MFST.ASK: {
                    MIT.EXACT:           MFST.COMPLETED,
                    MIT.EXACT_AND_OTHER: MFST.COMPLETED,
                    MIT.MATCHING:        MFST.CONFIRM,
                    MIT.OTHER:           MFST.ASK_CHOICE,
                },
                MFST.ASK_OPEN: {
                    MIT.OTHER: MFST.COMPLETED,
                },
                MFST.ASK_CHOICE: {
                    MIT.EXACT: MFST.COMPLETED,
                    MIT.OTHER: MFST.CLARIFY_AC,
                },
                MFST.CLARIFY_C: {
                    MIT.AGREE: MFST.COMPLETED,
                    MIT.OTHER: MFST.CLARIFY_C,
                },
                MFST.CLARIFY_AC: {
                    MIT.EXACT: MFST.COMPLETED,
                    MIT.OTHER: MFST.CLARIFY_AC,
                },
                MFST.COMPLETED: {
                    MIT.OTHER: MFST.COMPLETED,
                },
                MFST.CONFIRM: {
                    MIT.AGREE:    MFST.COMPLETED,
                    MIT.DISAGREE: MFST.ASK_CHOICE,
                    MIT.OTHER:    MFST.CLARIFY_C,
                }
            },
            EIT.DUAL: {
                MFST.ASK: {
                    MIT.EXACT:           MFST.ASK_OPEN,
                    MIT.EXACT_AND_OTHER: MFST.COMPLETED,
                    MIT.MATCHING:        MFST.CONFIRM,
                    MIT.OTHER:           MFST.ASK_CHOICE,
                },
                MFST.ASK_OPEN: {
                    MIT.OTHER: MFST.COMPLETED,
                },
                MFST.ASK_CHOICE: {
                    MIT.EXACT: MFST.COMPLETED,
                    MIT.OTHER: MFST.CLARIFY_AC,
                },
                MFST.CLARIFY_C: {
                    MIT.AGREE: MFST.COMPLETED,
                    MIT.DISAGREE: MFST.ASK_CHOICE,
                    MIT.OTHER: MFST.CLARIFY_C,
                },
                MFST.CLARIFY_AC: {
                    MIT.EXACT: MFST.COMPLETED,
                    MIT.OTHER: MFST.CLARIFY_AC,
                },
                MFST.COMPLETED: {
                    MIT.OTHER: MFST.COMPLETED,
                },
                MFST.CONFIRM: {
                    MIT.AGREE:    MFST.COMPLETED,
                    MIT.DISAGREE: MFST.ASK_CHOICE,
                    MIT.OTHER:    MFST.CLARIFY_C,
                }
            },
            EIT.OPEN: {
                MFST.ASK: {
                    MIT.OTHER: MFST.COMPLETED,
                }
            }
        }

    def next_state(self, eit: EIT, mfst: MFST, mit: MIT) -> MFST:
        ret: MFST = None
        if mit in self.flow[eit][mfst].keys():
            ret = self.flow[eit][mfst][mit]
        elif MIT.OTHER in self.flow[eit][mfst].keys():
            ret = self.flow[eit][mfst][MIT.OTHER]
        if ret is None:
            raise Exception(f'Unknown input type {mit} for matter flow state {mfst}')
        return ret
