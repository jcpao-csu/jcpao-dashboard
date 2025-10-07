# dv_data.py

# Comprehensive analysis of cases we receive from law enforcement agencies related to domestic violence 

# For now, begin tracking cases: domestic assaults, from 01-14-2025 onwards 

* relation_type (str): category of relationship between parties (relationship of defendant to victim)
    - Current spouse
    - Ex-spouse
    - Current romantic partner (s/o) *s/o can include spouses, long-term partners...
    - Ex-romantic partner (s/o)
    - Dating 
    - Same-sex / gender-diverse relationships

    - Parent
    - Child
    - Siblings
    - Extended family
    - Legal guardians / other custodial figures

    - Former intimate partners targeting current partner of their ex

(Intimate Partner Violence) - IPVI
  * Current spouse / Ex-spouse (divorced)
  * Current romantic partner / Ex-romantic partner (girlfriend/boyfriend)
  * Dating partner (regardless of cohabitation)
  * Individuals in same-sex or gender-diverse relationships

(Familial / Intra-family Violence)
  * Parent/child (step- and adoptive children)
  * Siblings 
  * Extended family (grandparents, cousings, in-laws)
  * Legal guardians, or other custodial figures

(Former Partners toward New Partners)
* Former intimate partners targeting the current partner of their ex 
* Stalking, harassment, or physical violence aimed at the new partner 

(Household Violence, Non-familial)


* abuse_type (str): category of abuse committed
  * Physical - hitting, slapping, choking, pushing, restraining
  * Sexual - sexual assault, coercion, unwanted contact (not: consensual)
  * Emotional/psychological - threats, gaslighting, name-calling, intimidation
  * Verbal - yelling, derogatory language, threats
  * Financial/economic - withholding money, controlling access to resources
  * Digital - monitoring devices, abusive texts/emails/social media activity
  * Stalking or harassment - repeated, unwanted attention, following, threats
  * Coercive control - patterns of manipulation, surveillance, restriction of liberty
  * Threats to third parties - children, pets, current partners 

* firearm (bool): was firearm involved? 
* shots_fired (bool): were shots fired?
* homicide (bool): homicide? 
* bts (bool): bullet-to-skin?
* firearm_type (str): type of handgun (whatever information can be obtained)
* previous_history (bool): not first time / previous reports of dv? 

* contexual indicators??
  * Protective orders or restraining orders
  * Custody disputes involving DV allegations
  * Reports or records involving the same parties over time
  * Police reports, 911 calls, hospital records with relationship-based identifiers 
  * History of repeat incidents across different jurisdictions involving same individuals 

* Criteria:
  * broken bones,
  * stitches/staples,
  * physical pain that is provable,
  * strangulation,
  * children witnessed assault or were injured,
  * defendant currently has DV case being investigated or pending state level charges, or pending municipal charge where there appears to be escalation,
  * defendant is on probation for a DV-related offense (either state or municipal probation),
  * victim is elderly, pregnant, disabled,
  * firearms involved,
  * kidnapping,
  * pattern of stalking,
  * two separate DV incidents within 12 hours that shows escalation of violence,
  * three or more prior charged municipal DV related violations of orders of protection