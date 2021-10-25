import { ApolloLink } from '@apollo/client/link/core';
import { Subscriber } from '@graphql-tools/delegate';
export declare const linkToSubscriber: (link: ApolloLink) => Subscriber;
