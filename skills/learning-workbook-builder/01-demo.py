# %% [markdown]
# # Module 01 — demo
# ```mermaid
# flowchart LR
#   A[estimators] --> C[cvar]
# ```
# %%
from checks import check_fn
def mse(var, bias):
    return None  # TODO
check_fn("mse = var + bias^2", mse, lambda v,b: v + b*b, [(1,2),(0.5,0.5)])
