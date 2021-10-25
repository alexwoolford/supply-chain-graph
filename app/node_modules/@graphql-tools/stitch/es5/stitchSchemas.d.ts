import { GraphQLSchema } from 'graphql';
import { IStitchSchemasOptions } from './types';
export declare function stitchSchemas({ subschemas, types, typeDefs, onTypeConflict, mergeDirectives, mergeTypes, typeMergingOptions, subschemaConfigTransforms, resolvers, schemaDirectives, inheritResolversFromInterfaces, logger, allowUndefinedInResolve, resolverValidationOptions, directiveResolvers, schemaTransforms, parseOptions, pruningOptions, updateResolversInPlace, }: IStitchSchemasOptions): GraphQLSchema;
