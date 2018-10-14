# Quantum Disconsensus

Hackathon project on quantum leadership election protocols by the Quantum
Disconsensus team.

All code developed as part of this hackathon has been submitted upstream to the
SimulaQron GitHub repository in [this pull
request](https://github.com/SoftwareQuTech/SimulaQron/pull/90).

## Motivation

Consensus protocols, and in particular leadership election, are very important
in classical distributed system.  Here, we implement two quantum leadership
protocols.

## Coin Flip Leader Election

It is possible to elect a leader from a collection of N nodes by performing a
series of coin flips as explained in [this
paper](https://arxiv.org/abs/0910.4952v2).

## W State Leader Election

A conceptually simple way to elect a leader of N nodes is to prepare a W state
of N qubits and distribute one qubit to each node.  Each node measures their
qubit and the node that measures `1` becomes the leader.  The idea comes from
[this presentation](https://ww2.chemistry.gatech.edu/pradeep/talks/qle.pdf).

In order to run this protocol, it is necessary to prepare a W state.  The W
state preparation is based on [this paper](https://arxiv.org/abs/1807.05572).