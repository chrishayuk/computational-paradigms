# P16. Shared information at scale

*Added after review 2.*

**Probes:** how a system resolves a large structure of relations
contributed independently, propagates one new fact through it, works
together with several contributors, confines work to the part that new
information affects, and detects a contradiction.

The problem states only relations and outcomes. It does not prescribe
processes, a shared store or any other mechanism. A system may use
whatever algorithm is its own, including one that collects every relation
and solves them at once.

## Vocabulary

All unknowns are integers. succ(a, b) is the relation b = a + 1.

Sizes: n = 10², 10³ and 10⁴, fixed in advance. Limits as in P13: a budget
of 10⁸ steps per stage and a safety limit of 600 seconds, not raised for
any system.

**Arrival orders.** Where relations arrive as a collection, they arrive in
one of three orders, fixed here:

- **ascending:** succ(x₁, x₂), succ(x₂, x₃), …;
- **descending:** the same, last first;
- **interleaved:** the relations with odd i ascending, then those with
  even i ascending.

## P16a. Propagation along a chain

| stage | information | valid outcomes |
|---|---|---|
| 1 | succ(xᵢ, xᵢ₊₁) for i = 1, …, n − 1, in the given order | xᵢ = x₁ + i − 1, for every integer x₁ |
| 2 | x_j = 0, where j = ⌈n/2⌉ | xᵢ = i − j, for every i |

One fact at stage 2 determines the whole chain.

## P16b. Several contributors

There are four contributors and m = n/4. Contributor c, for c = 1 to 4,
contributes succ(xᵢ, xᵢ₊₁) for i = (c − 1)m + 1, …, cm, in ascending order.
So there are n relations over the n + 1 unknowns x₁, …, xₙ₊₁. Neighbouring
contributors share the unknown at the boundary between their segments. Each contributor is a separate computation (`spawn`), where the
configuration allows separate computations to share unknowns. Where it
does not, the four are posed as one conjunction, and that is recorded.

| stage | information | valid outcomes |
|---|---|---|
| 1 | the four contributions | xᵢ = x₁ + i − 1 |
| 2 | total = x₁ + x_{m+1} + x_{2m+1} + x_{3m+1} + x_{4m+1} | as stage 1, with total = 5x₁ + 10m |
| 3 | x₁ = 0 | xᵢ = i − 1; total = 10m |

The relation of stage 2 needs information from every contributor.

## P16c. Localised updates

Two chains, of n unknowns each, that share no unknown: x₁, …, xₙ and
y₁, …, yₙ.

| stage | information | valid outcomes |
|---|---|---|
| 1 | every succ(xᵢ, xᵢ₊₁) and succ(yᵢ, yᵢ₊₁), the x relations first, ascending | each chain determined up to its first element |
| 2 | x₁ = 0 | xᵢ = i − 1; y still determined only up to y₁ |
| 3 | y₁ = 5 | xᵢ = i − 1; yᵢ = i + 4 |

The measure that matters is how much of the y chain is examined at stage
2, and how much of the x chain at stage 3. Ideally neither is.

## P16d. Contradiction

Two chains, as in P16c.

| stage | information | valid outcomes |
|---|---|---|
| 1 | every succ for both chains, ascending | as P16c stage 1 |
| 2 | x₁ = 0 | as P16c stage 2 |
| 3 | xₙ = 0 | none, since xₙ = n − 1 ≠ 0 |

**P16d2** is the same, with stage 2 omitted and stage 3 replaced by
xₙ = x₁. That contradicts the chain without any value being known
(xₙ = x₁ + n − 1). Detecting it requires combining relations, as P07f
does.

The y chain is not involved in either contradiction. If it is posed as a
separate computation, its outcome is valid on its own. If it is posed in
the same conjunction, the conjunction has no solution.

## Observations

- Problem operations: how many times each succ relation is examined, in
  total and per stage. Each needs to be decided only once after its first
  value is known.
- Repeated work: relations examined again without new information about
  them.
- Suspended state: relations held, at each stage boundary and at their
  peak.
- For P16c: examinations of the uninvolved chain at each stage.
- For P16d and P16d2: whether the contradiction is detected, at which
  stage, and in how many steps after its last relation arrives. What
  happens to the y chain.
- The growth of steps, problem operations and store with n, compared
  across systems as `METRICS.md` says, for each arrival order.
