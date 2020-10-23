import pandas as pd
import numpy as np
import os
from scipy.stats import normaltest


class DcnaTool:

    def __init__(self):
        pass

    def read_input(self, input_folder, file):

        filename, file_ext = os.path.splitext(os.path.basename(file))
        df = pd.read_excel(input_folder + file, header=None)
        # Ortalama aliyoruz
        df = df.groupby(df.columns[0]).mean().reset_index()
        # Gen isimlerimin bulundugu kolonu siliyoruz ki normalizasyon yapabilelim.
        df_values = df.iloc[:, 1:]
        # Gen isimlerini alıyoruz
        df_genes = df.iloc[:, 0]

        return filename, df_genes, df_values

    def normalization(self, df_values):

        # Sutun bazinda ortalama aliyoruz. axis=1 olursa satir bazinda ortalama alir.
        mean = df_values.mean(axis=0)
        # Sutun bazinda standart sapma aliyoruz.
        std = df_values.std(axis=0)
        # Normalizasyon
        df_norm = ((df_values - mean) / std)

        return df_norm

    def explode_samples(self, normalizated_data, healthy_sample):

        # sağlıklı ve hastalıklı örnekleri bölüyoruz.
        healthy = normalizated_data.iloc[:, 0:int(healthy_sample)]
        disease = normalizated_data.iloc[:, int(healthy_sample):]
        # örnek sayıları
        disease_sample = len(disease.columns)
        healthy_sample = len(healthy.columns)

        return healthy, disease, disease_sample, healthy_sample

    def normality_test(self, healthy, disease):

        z_h, pval_healthy = normaltest(healthy.stack().to_numpy())
        z_d, pval_disease = normaltest(disease.stack().to_numpy())

        return pval_healthy, pval_disease

    def correlation(self, healthy, pval_healthy, disease, pval_disease):

        # Pearson ve Spearman uyguluyoruz.
        if (pval_healthy < 0.05):
            healthy_corr = healthy.T.corr(method='spearman')
        else:
            healthy_corr = healthy.T.corr()
        if (pval_disease < 0.05):
            disease_corr = disease.T.corr(method='spearman')
        else:
            disease_corr = disease.T.corr()

        return healthy_corr, disease_corr

    def find_pcritic(self, healthy_corr, disease_corr):

        # Sağlıklı bölümler
        df_healty_mean = healthy_corr.values[np.triu_indices_from(healthy_corr.values, 1)].mean()
        df_healty_std = healthy_corr.values[np.triu_indices_from(healthy_corr.values, 1)].std()
        pcritic_healty = df_healty_mean + 1.96 * df_healty_std
        # Hastalıklı bölümler
        df_disease_mean = disease_corr.values[np.triu_indices_from(disease_corr.values, 1)].mean()
        df_disease_std = disease_corr.values[np.triu_indices_from(disease_corr.values, 1)].std()
        pcritic_disease = df_disease_mean + 1.96 * df_disease_std
        # İki pcritic değerinden ufak olanı seçiyoruz.
        pcritic = min(pcritic_healty, pcritic_disease)

        if (pcritic > 0.7):
            pcritic = 0.7

        return pcritic, pcritic_healty, pcritic_disease

    def make_binary(self, healthy_corr, disease_corr, df_genes):

        # Pearson Uygulanmış temiz verinin satır ve sütunlarına gen isimlerini ekliyoruz.
        healthy_with_genes = pd.DataFrame(healthy_corr.values, index=df_genes.values, columns=df_genes.values)
        disease_with_genes = pd.DataFrame(disease_corr.values, index=df_genes.values, columns=df_genes.values)

        # Veriyi binary dizi haline getiriyoruz.
        # melted = pd.melt(df_healty2.reset_index(), id_vars='index', value_vars=df_genes.values)
        dfHealty = healthy_with_genes.stack().reset_index()
        dfHealty.columns = ['gene1', 'gene2', 'score']
        dfDisease = disease_with_genes.stack().reset_index()
        dfDisease.columns = ['gene1', 'gene2', 'score']

        dfDisease['opposite'] = dfHealty['score']
        dfHealty['opposite'] = dfDisease['score']

        # Genlerin kendileri ile olan eşleşmelerini siliyoruz
        df_healthy_filter = dfHealty[dfHealty.gene1 != dfHealty.gene2]
        df_disease_filter = dfDisease[dfDisease.gene1 != dfDisease.gene2]

        # Tekrarlayan capraz gen satırlarını siliyoruz
        h_filter = pd.DataFrame(df_healthy_filter, columns=['gene1', 'gene2', 'score', 'opposite'])
        h_filter = h_filter[h_filter['gene1'] < h_filter['gene2']]

        d_filter = pd.DataFrame(df_disease_filter, columns=['gene1', 'gene2', 'score', 'opposite'])
        d_filter = d_filter[d_filter['gene1'] < d_filter['gene2']]

        return h_filter, d_filter

    def filter_by_pcritic(self, healthy_binary, disease_binary, pcritic):

        # Pcritic değerlerinden büyük olan Anlamlı verileri filtreliyoruz
        filtred_healthy = healthy_binary[(healthy_binary.score > pcritic) | (-healthy_binary.score > pcritic)].reset_index(drop=True)
        filtred_disease = disease_binary[(disease_binary.score > pcritic) | (-disease_binary.score > pcritic)].reset_index(drop=True)

        return filtred_healthy, filtred_disease

    def differential_co_expression(self, healthy, disease, pcritic, threshold):

        healthy['differential'] = healthy['score'] - healthy['opposite']
        healthy = healthy[(healthy['opposite'] < pcritic) | (healthy['differential'] > threshold)]
        healthy = healthy[(healthy['opposite'] > -pcritic) | (healthy['differential'] > threshold)]
        healthy = healthy.sort_values(by="opposite", ascending=False).reset_index(drop=True)

        disease['differential'] = disease['score'] - disease['opposite']
        disease = disease[(disease['opposite'] < pcritic) | (disease['differential'] > threshold)]
        disease = disease[(disease['opposite'] > -pcritic) | (disease['differential'] > threshold)]
        disease = disease.sort_values(by="opposite", ascending=False).reset_index(drop=True)

        return healthy, disease

    def export_excel(self, filename, folder, healthy, disease):

        healthy.to_excel(folder + 'healthy_' + filename + '.xlsx', engine='xlsxwriter', index=None, header=True)
        disease.to_excel(folder + 'disease_' + filename + '.xlsx', engine='xlsxwriter', index=None, header=True)

    def export_json(self, healthy, disease):

        # if (len(healthy.values) == 0):
        #     raise ValueError('Result is Empty.')
        return healthy.to_json(), disease.to_json()

    def interaction_count(self, healthy, disease):

        return len(healthy.index), len(disease.index)

    def find_module_interactions(self, df, cluster):

        interactions = df.loc[(df['gene1'].isin(cluster)) & (df['gene2'].isin(cluster))].reset_index(drop=True)
        return interactions[interactions['gene1'] < interactions['gene2']]
