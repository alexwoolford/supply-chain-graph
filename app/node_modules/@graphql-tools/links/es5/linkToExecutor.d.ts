import { ApolloLink } from '@apollo/client/link/core';
import { Executor } from '@graphql-tools/delegate';
export declare const linkToExecutor: (link: ApolloLink) => Executor;
